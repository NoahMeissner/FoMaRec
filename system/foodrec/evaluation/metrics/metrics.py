# Noah Meissner 17.08.2025

"""
    This file is responsible for the metric calculation of the biase evaluation.
"""
from typing import List, Dict


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

