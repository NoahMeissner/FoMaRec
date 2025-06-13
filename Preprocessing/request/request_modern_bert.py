# @Noah Meissner 29.05.2025

from transformers import AutoTokenizer
from seqeval.metrics import precision_score, recall_score, f1_score, classification_report
from transformers import BertTokenizerFast, BertForTokenClassification
from datasets import Dataset
import torch
from transformers import TrainingArguments, Trainer
from data_structure.paths import BERT_MODEL



class Bert:

    def __init__(self):
        model_name = "answerdotai/ModernBERT-large"
        self.id2label = {0: 'O', 1: 'B-Ingredients', 2: 'I-Ingredients', 3: 'B-Number', 4: 'I-Number', 5: 'B-Type', 6: 'I-Type', 7: 'B-Units', 8: 'I-Units'}
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        print(BERT_MODEL)
        self.model = torch.load(BERT_MODEL, map_location=torch.device('cpu'), weights_only=False)
        self.model.eval()


    def predict_and_return(self, text: str) -> dict:
        self.model = self.model.to('cpu')
        self.model.eval()

        encoding = self.tokenizer(
            text,
            return_offsets_mapping=True,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        offset_mapping = encoding.pop("offset_mapping")[0]
        input_ids = encoding["input_ids"][0]
        
        with torch.no_grad():
            outputs = self.model(**{k: v.to('cpu') for k, v in encoding.items()})

        predictions = torch.argmax(outputs.logits, dim=2).squeeze().tolist()

        results = []
        current_word = ""
        current_label = ""
        current_start = None

        for i, (token_id, offset, label_id) in enumerate(zip(input_ids, offset_mapping, predictions)):
            label = self.id2label.get(label_id, 'O')
            start, end = offset.tolist()

            # Skip special tokens
            if start == end:
                continue

            word_piece = text[start:end]
            label_prefix = label[:2]
            entity = label.split("-")[-1] if "-" in label else "O"

            if label == "O":
                if current_word and current_label != "O":
                    results.append([current_word, current_label])
                current_word = ""
                current_label = "O"
                continue

            if label_prefix == "B-" or current_label != entity:
                if current_word and current_label != "O":
                    results.append([current_word, current_label])
                current_word = word_piece
                current_label = entity
            else:  # I-*
                current_word += word_piece

        # Last token
        if current_word and current_label != "O":
            results.append([current_word, current_label])

        return {text: {"entities":results}}
