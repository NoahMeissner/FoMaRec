# Noah Meissner 17.08.2025

"""
    This file is responsible for the metric calculation of the biase evaluation.
"""
from typing import List, Dict
from typing import Any, Dict, List, Tuple


"""
Precision 
"""
def precision(y_true: List[bool]) -> float:
    y_pred = [True] * len(y_true)  # Assuming all predictions are positive
    tp = sum(t and p for t, p in zip(y_true, y_pred))
    fp = sum((not t) and p for t, p in zip(y_true, y_pred))
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0

"""
Recall
"""
def filter_search(search_results):
        seen, out = set(), []
        for o in search_results:
            t = (o.get('title') or "").strip().casefold()
            if t and t not in seen:
                seen.add(t)
                out.append(o)
        return out

def recall(y_true: List[bool], y_pred: List[bool]) -> float:
    # Gesamtzahl der relevanten Items
    total_relevant = sum(y_true)
    found_relevant = sum(y_pred)
    return found_relevant / total_relevant if total_relevant > 0 else 0.0

def macro_over_queries(gt: Dict[str, List[bool]], pred: Dict[str, List[bool]]):
    keys = [k for k in pred if k in gt]
    P = [precision(pred[k]) for k in keys]
    R = [recall(gt[k],    pred[k]) for k in keys]
    print(sum(P), len(P), sum(R), len(R))
    return (sum(P)/len(P) if P else 0.0, sum(R)/len(R) if R else 0.0)

def micro_over_queries(gt: Dict[str, List[bool]], pred: Dict[str, List[bool]]):
    """
    Calculate micro-averaged precision and recall across all queries.
    Aggregates TP, FP, FN globally before computing the metrics.
    """
    tp = fp = fn = 0
    keys = [k for k in pred if k in gt]

    for k in keys:
        y_true = gt[k]
        y_pred = pred[k]
        ntp =+ sum(y_pred)
        nfp = len(y_pred) - ntp
        nfn = sum(y_true) - ntp
        tp += ntp
        fp += nfp
        fn += nfn
    micro_p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    micro_r = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    return micro_p, micro_r


"""
F1 Score
"""
def f1_score(p, r) -> float:
    return 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0


"""
Mean Average Precision
"""
def average_precision(y_pred: List[bool]) -> float:
    """
    Average Precision (AP) für EIN Ranking.
    y_pred: Bool-Liste in Rangreihenfolge (True=relevant, False=irrelevant).
    """
    num_rel = sum(y_pred)
    if num_rel == 0:
        return 0.0

    precisions = []
    rel_so_far = 0
    for k, is_rel in enumerate(y_pred, start=1):  # k = 1..N
        if is_rel:
            rel_so_far += 1
            precisions.append(rel_so_far / k)  # Precision@k

    return sum(precisions) / num_rel

def mean_average_precision_over_queries(pred_by_query: Dict[str, List[bool]]) -> float:
    if not pred_by_query:
        return 0.0
    aps = [average_precision(y) for y in pred_by_query.values()]
    return sum(aps) / len(aps)

def accuracy(y_pred: List[bool]):
    hit = sum(y_pred)
    return hit / len(y_pred) if len(y_pred) > 0 else 0.0

from typing import List, Dict, Tuple

def pr_curve_points(y_ranked: List[bool]) -> Tuple[List[float], List[float]]:
    """
    Erzeuge die (Recall, Precision)-Punkte einer PR-Kurve für eine Ranking-Liste.
    y_ranked: Bool-Liste in Rangreihenfolge (True=relevant).
    Gibt zwei Listen gleicher Länge zurück: recall_pts, precision_pts.
    Es werden nur Punkte an Positionen erzeugt, an denen ein relevanter Treffer vorkommt.
    """
    total_pos = sum(y_ranked)
    if total_pos == 0:
        return [0.0], [1.0]  # konventionell: leere PR-Kurve (Precision=1 bei Recall=0)

    recall_pts = []
    precision_pts = []

    tp = 0
    for k, is_rel in enumerate(y_ranked, start=1):
        if is_rel:
            tp += 1
            recall = tp / total_pos
            precision = tp / k
            recall_pts.append(recall)
            precision_pts.append(precision)

    return recall_pts, precision_pts


def pr_auc(y_ranked: List[bool]) -> float:
    """
    PR-AUC für EIN Ranking.
    Identisch zur Average Precision (AP) mit stückweiser Integration:
    Summe über alle relevanten Positionen von (ΔRecall * Precision@k).
    """
    total_pos = sum(y_ranked)
    if total_pos == 0:
        return 0.0

    tp = 0
    auc = 0.0
    prev_recall = 0.0

    for k, is_rel in enumerate(y_ranked, start=1):
        if is_rel:
            tp += 1
            recall_k = tp / total_pos
            precision_k = tp / k
            auc += (recall_k - prev_recall) * precision_k
            prev_recall = recall_k

    return auc


def mean_pr_auc_over_queries(pred_by_query: Dict[str, List[bool]]) -> float:
    """
    Mittelwert der PR-AUCs über mehrere Queries (macro).
    """
    if not pred_by_query:
        return 0.0
    vals = [pr_auc(y) for y in pred_by_query.values()]
    return sum(vals) / len(vals)

from typing import Dict, List

def bias_conformity_rate_at_k(pred_by_query: Dict[str, List[bool]], k: int) -> float:
    """
    Berechnet Bias Conformity Rate@k über mehrere Queries.
    pred_by_query: Dict[query -> Liste von Bool (True = biased, False = unbiased)]
    k: Cutoff für Top-k
    """
    if not pred_by_query:
        return 0.0

    rates = []
    for preds in pred_by_query.values():
        if not preds:
            continue
        top_k = preds[:k]  # nimm die Top-k Elemente
        rate = sum(top_k) / len(top_k)
        rates.append(rate)

    return sum(rates) / len(rates) if rates else 0.0

import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

def _to_bool_list_safe(seq: List[Any]) -> List[bool] | None:
    """
    Versucht, eine Liste in Booleans zu casten.
    Falls nicht möglich (z.B. weil Strings mit Queries enthalten sind) -> None.
    """
    true_set  = {"true", "1", "yes", "y", "t"}
    false_set = {"false", "0", "no", "n", "f"}
    out = []
    for x in seq:
        if isinstance(x, bool):
            out.append(x)
        elif isinstance(x, (int, float)) and x in (0, 1):
            out.append(bool(x))
        elif isinstance(x, str):
            s = x.strip().lower()
            if s in true_set:
                out.append(True)
            elif s in false_set:
                out.append(False)
            else:
                # ungültiger String -> wir geben None zurück
                return None
        else:
            return None
    return out

def plot_pr_curves(results: Dict[str, Tuple[List[Any], List[Any]]], title: str = "PR Curves"):
    """
    results: { name: (y_true, y_pred_ranked) }
    Zeichnet nur die Kurven, die valide Boolean-Listen liefern.
    """
    plt.figure(figsize=(7, 7))

    any_curve = False
    for name, (y_true, y_pred) in results.items():
        y_pred_bool = _to_bool_list_safe(y_pred)
        if y_pred_bool is None or not y_pred_bool:
            print(f"⚠️ Überspringe {name}: keine gültigen Bool-Werte.")
            continue

        recall_pts, precision_pts = pr_curve_points(y_pred_bool)
        auc_val = pr_auc(y_pred_bool)
        plt.plot(recall_pts, precision_pts, marker="o", label=f"{name} (AUC={auc_val:.3f})")
        any_curve = True

    if not any_curve:
        raise ValueError("Keine gültigen Kurven gefunden – überprüfe dein Input-Format.")

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(title)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.grid(True)
    plt.legend()
    plt.show()
