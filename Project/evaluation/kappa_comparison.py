from sklearn.metrics import cohen_kappa_score, accuracy_score, f1_score, matthews_corrcoef, jaccard_score
from tabulate import tabulate
import re
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import numpy as np

def tokenize(text):
    return re.findall(r'\w+|[^\w\s]', text, re.UNICODE)

def get_token_labels(text, entities):
    tokens = tokenize(text)
    labels = ['O'] * len(tokens)  
    for ent_text, ent_label in entities:
        ent_tokens = tokenize(ent_text)
        for i in range(len(tokens) - len(ent_tokens) + 1):
            if tokens[i:i+len(ent_tokens)] == ent_tokens:
                for j in range(i, i+len(ent_tokens)):
                    labels[j] = ent_label.lower()
    return tokens, labels

def prepare_labels_for_texts(dict_one, dict_two):
    all_texts = set(dict_one.keys()).union(dict_two.keys())
    all_labels_one = []
    all_labels_two = []
    all_tokens = []

    for text in all_texts:
        entities_one = dict_one.get(text, [])
        entities_two = dict_two.get(text, [])

        tokens, labels_one = get_token_labels(text, entities_one)
        _, labels_two = get_token_labels(text, entities_two)

        if len(labels_one) != len(labels_two):
            min_len = min(len(labels_one), len(labels_two))
            labels_one = labels_one[:min_len]
            labels_two = labels_two[:min_len]
            tokens = tokens[:min_len]

        all_labels_one.extend(labels_one)
        all_labels_two.extend(labels_two)
        all_tokens.extend(tokens)

    return all_tokens, all_labels_one, all_labels_two


def print_metrics_table(label_metrics):
    headers = ["Metric", "Score"]
    table = []
    for metric, score in label_metrics.items():
        table.append([metric, f"{score:.4f}"])
    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))


def evaluate_annotations(ls_one, ls_two):
    dict_one = make_one_dict(ls_one)
    dict_two = make_one_dict(ls_two)

    tokens, labels_one, labels_two = prepare_labels_for_texts(dict_one, dict_two)

    if len(set(labels_one)) < 2 or len(set(labels_two)) < 2:
        print("⚠️ Wenig Klassenvielfalt für Kappa.")
        return

    print("\n📈 Metriken:")
    metrics = {
        "Accuracy": accuracy_score(labels_one, labels_two),
        "F1": f1_score(labels_one, labels_two, average='weighted'),
        "MCC": matthews_corrcoef(labels_one, labels_two),
        "Jaccard": jaccard_score(labels_one, labels_two, average='weighted'),
        "Cohen's Kappa": cohen_kappa_score(labels_one, labels_two)
    }
    print_metrics_table(metrics)
    print(30*"=")
    print("\n🧮 Konfusionsmatrix:\n")
    labels = sorted(set(labels_one + labels_two))
    cm = confusion_matrix(labels_one, labels_two, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    print(cm_df)

def make_one_dict(ls):
    dict = {}
    for value in ls:
        key = list(value.keys())[0]
        dict[key] = value[key]['entities']
    return dict
