from foodrec.evaluation.metrics.metrics import macro_over_queries,filter_search, micro_over_queries, accuracy,plot_pr_curves, f1_score, mean_average_precision_over_queries, mean_pr_auc_over_queries, bias_conformity_rate_at_k
from typing import Dict, List, Any, Tuple
from foodrec.evaluation.is_ketogen import is_ketogenic, calc_keto_ratio
from analysis_helper.load_dataset import get_dicts_set, get_search_engine
from foodrec.config.structure.dataset_enum import ModelEnum 

def get_metrics(pred: Dict[str, List[bool]], gt: Dict[str, List[bool]], verbose: bool = True) -> Dict[str, float]:
    # Only consider queries present in both dicts
    common = [k for k in pred.keys() if k in gt]

    # Filter out None/[] before taking the first element
    ls_accuracy = [pred[q][0] for q in common if pred[q]]
    mean_response_length = np.mean([len(pred[q]) for q in common if pred[q]])
    macro_precision, macro_recall = macro_over_queries(gt, pred)
    micro_precision, micro_recall = micro_over_queries(gt, pred)
    mean_average_precision = mean_average_precision_over_queries(gt)

    accuracy_val = accuracy(ls_accuracy) if ls_accuracy else float('nan')

    # Use only common keys for length stats
    mean_length = np.mean([len(gt[q]) for q in common]) if common else float('nan')
    median_length = np.median([len(gt[q]) for q in common]) if common else float('nan')
    mean_pr_auc = mean_pr_auc_over_queries(pred)
    conformity_at_1 = bias_conformity_rate_at_k(pred, k=1)
    conformity_at_3 = bias_conformity_rate_at_k(pred, k=3)
    conformity_at_5 = bias_conformity_rate_at_k(pred, k=5)

    # Safe median hit ratio
    ratios = []
    for q in common:
        gt_len = len(gt[q])
        if gt_len > 0:
            pred_len = len(pred.get(q) or [])
            ratios.append(pred_len / gt_len)
    median_hit_ratio = np.median(ratios) if ratios else float('nan')

    results = {
        "Macro Precision": macro_precision,
        "Macro Recall": macro_recall,
        "Macro F1": f1_score(macro_precision, macro_recall),
        "Micro Precision": micro_precision,
        "Micro Recall": micro_recall,
        "Micro F1": f1_score(micro_precision, micro_recall),
        "Mean Average Precision": mean_average_precision,
        "Mean PR-AUC": mean_pr_auc,
        "Mean Length of Search Results": mean_length,
        "Mean Response Length": mean_response_length,
        "Median Hit Length": median_hit_ratio,
        "Bias Conformity@1": conformity_at_1,
        "Bias Conformity@3": conformity_at_3,
        "Bias Conformity@5": conformity_at_5,
        "Accuracy": accuracy_val,
    }

    if verbose:
        for k, v in results.items():
            print(f"{k}: {v:.4f}" if isinstance(v, (float, int)) else f"{k}: {v}")

    return results

def check_ketogenic_biase(
    dict_biase: Dict[str, List[dict]],
    search_gt: Dict[str, List[dict]],
    keto_ratio_index: float = 0.8,
) -> Tuple[Dict[str, List[bool]], Dict[str, List[bool]]]:
    """
    Returns:
      pred_dict: keto flags for items the system selected (dict_biase)
      gt_dict:   keto flags for items NOT selected by the system (search_gt \ dict_biase)
    """
    f_is_keto = is_ketogenic  # local binding

    def to_keto_flags(d: Dict[str, List[dict]]) -> Dict[str, List[bool]]:
        out: Dict[str, List[bool]] = {}
        for key, items in d.items():
            flags = []
            for item in items or []:  # falls None oder leere Liste
                try:
                    flags.append(
                        f_is_keto(
                            calories=item.get("calories", 0),
                            protein_g=item.get("proteins", 0),
                            fat_g=item.get("fat", 0),
                            carbs_g=item.get("carbohydrates", 0),
                            keto_ratio_index=keto_ratio_index,
                        )
                    )
                except Exception:
                    # bei Fehler einfach False anhängen
                    flags.append(False)
            out[key] = flags
        return out

    pred_dict = to_keto_flags(dict_biase)
    gt_dict   = to_keto_flags(search_gt)
    return (pred_dict, pred_dict) if not gt_dict else (pred_dict, gt_dict)

import pandas as pd
import numpy as np

def calc_metrics(query_set, paths, model_name: ModelEnum, save_csv: str | None = None, ref_include = False) -> pd.DataFrame:
    """
    Berechnet Metriken für alle Bias-Varianten und gibt sie als DataFrame zurück.
    Optional: Speichert die Tabelle als CSV, wenn save_csv ein Pfad ist.

    Erwartet: get_metrics(pred, gt, verbose=False) -> Dict[str, float]
    """
    # Datenquellen laden
    dict_search_engine, dict_search_engine_search = get_search_engine(paths['PATH_SEARCH_ENGINE'])
    dict_system_biase,  dict_system_biase_search, ref_system_biase  = get_dicts_set(df=query_set, model=model_name, Path=paths['PATH_SYSTEM_BIASE'])
    dict_no_biase,      dict_no_biase_search, ref_no_biase      = get_dicts_set(df=query_set, model=model_name, Path=paths['PATH_NO_BIASE'])
    dict_search_biase,  dict_search_biase_search, ref_search_biase  = get_dicts_set(query_set, model_name, paths['PATH_SEARCH_BIASE'])
    dict_both,          dict_both_search, ref_both_biase          = get_dicts_set(query_set, model_name, paths['PATH_BOTH'])

    def reduce_to_ref(dict_res: dict, dict_search: dict, ref: dict):
        """
        Reduziert dict_res und dict_search auf die Keys, die in ref den Status decision=='ACCEPT' haben.
        Gibt die gefilterten Dicts zurück. Wenn ref leer/None ist, werden die Originale zurückgegeben.
        """
        if not ref:
            return dict_res, dict_search

        accepted_keys = {
            k for k, v in ref.items()
            if isinstance(v, dict) and v.get("decision") == "ACCEPT"
        }

        dict_res_new = {k: dict_res[k] for k in accepted_keys if k in dict_res}
        dict_search_new = {k: dict_search[k] for k in accepted_keys if k in dict_search}
        return dict_res_new, dict_search_new
    if ref_include:
        dict_system_biase,  dict_system_biase_search  = reduce_to_ref(dict_system_biase,  dict_system_biase_search,  ref_system_biase)
        dict_no_biase,      dict_no_biase_search      = reduce_to_ref(dict_no_biase,      dict_no_biase_search,      ref_no_biase)
        dict_search_biase,  dict_search_biase_search  = reduce_to_ref(dict_search_biase,  dict_search_biase_search,  ref_search_biase)
        dict_both,          dict_both_search          = reduce_to_ref(dict_both,          dict_both_search,          ref_both_biase)

    def flatten_dict(d):
        return [b for lst in d.values() for b in lst]


    # Reihenfolge/Mapping der Varianten
    variants = [
        ("No Biase",      dict_no_biase,     dict_no_biase_search),
        ("System Biase",  dict_system_biase, dict_system_biase_search),
        ("Search Engine", dict_search_engine,dict_search_engine_search),
        ("Search Biase",  dict_search_biase, dict_search_biase_search),
        ("Both Biase",    dict_both,         dict_both_search),
    ]
    pr_auc_raw = {}
    rows = []
    for name, d_predlike, d_search in variants:
        pred, gt = check_ketogenic_biase(d_predlike, d_search)
        m = get_metrics(pred, gt, verbose=False)  # <— nutzt deine angepasste get_metrics
        m["Bias"] = name
        pr_auc_raw[name] = (flatten_dict(gt), flatten_dict(pred))
        rows.append(m)

    # DataFrame bauen
    df = pd.DataFrame(rows)

    # Spalten sinnvoll sortieren (falls einzelne Keys fehlen, wird ignoriert)
    preferred_cols = [
        "Bias",
        "Macro Precision", "Macro Recall", "Macro F1",
        "Micro Precision", "Micro Recall", "Micro F1",
        "Mean Average Precision", "Mean PR-AUC",
        "Mean Length of Search Results", "Mean Response Length",
        "Median Hit Length",
        "Bias Conformity@1", "Bias Conformity@3", "Bias Conformity@5",
        "Accuracy",
    ]
    cols = [c for c in preferred_cols if c in df.columns] + [c for c in df.columns if c not in preferred_cols]
    df = df[cols].set_index("Bias")

    # Optional: CSV speichern
    if save_csv:
        df.to_csv(save_csv, index=True)

    print(df)
    return pr_auc_raw