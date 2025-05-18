import spacy
from spacy.tokens import DocBin
from spacy.training import Example
from spacy.util import minibatch, compounding
import random

LABELS = ["wrong", "type", "ingredients"]

def filter_overlapping_spans(spans):
    spans = sorted(spans, key=lambda span: (span.start, -span.end))
    filtered = []
    last_end = -1
    for span in spans:
        if span.start >= last_end:
            filtered.append(span)
            last_end = span.end
        else:
            print(f"Überschneidender Span entfernt: '{span.text}' ({span.start}, {span.end})")
    return filtered

def create_training_data(train_data):
    nlp = spacy.blank("de")
    db = DocBin()

    for text, annot in train_data:
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annot.get("entities"):
            span = doc.char_span(start, end, label=label, alignment_mode="expand")
            if span is None:
                print(f"Warnung: Ungültiger Span im Text: '{text[start:end]}' ({start}, {end})")
            else:
                ents.append(span)
        ents = filter_overlapping_spans(ents)
        doc.ents = ents
        db.add(doc)
    return db

def train_ner(train_data, labels, iterations=20):
    nlp = spacy.blank("de")

    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    for label in labels:
        ner.add_label(label)

    optimizer = nlp.begin_training()

    for itn in range(iterations):
        random.shuffle(train_data)
        losses = {}
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

        for batch in batches:
            examples = []
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                examples.append(example)

            nlp.update(examples, sgd=optimizer, drop=0.2, losses=losses)

        print(f"Iteration {itn+1}/{iterations} - Losses: {losses}")

    return nlp

def train_model(TRAIN_DATA):
    db = create_training_data(TRAIN_DATA)
    db.to_disk("./train.spacy")
    print("Spacy erstellt Trainingsdaten")
    print("Trainiere NER-Modell...")
    nlp_model = train_ner(TRAIN_DATA, LABELS)
    print("Speichere Modell...")
    nlp_model.to_disk("model/ingredients_ner_model")
    return nlp_model

def test_model(input=None, model=None):
    if model is None:
        model = spacy.load("model/ingredients_ner_model")
    doc = model(input)
    for ent in doc.ents:
        print(ent.text, ent.label_)
