import spacy
from spacy.tokens import DocBin
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import re
from data_structure.paths import SPACY_MODEL, SPACY_TRAIN_DATA


LABELS = ["Number","Units", "Type", "Ingredients"]

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
        raw_entities = annot.get("entities", [])
        
        # Stufe 1: Filterung auf Zeichenebene
        filtered_entities = []
        for ent in sorted(raw_entities, key=lambda x: (x[0], -x[1])):
            start, end, label = ent
            if not any(s < end and e > start for s, e, _ in filtered_entities):
                filtered_entities.append(ent)
            else:
                print(f"⚠️ Überschneidung auf Zeichenebene entfernt: {ent}")

        # Stufe 2: Konvertierung zu Spans mit Token-Validierung
        spans = []
        for start, end, label in filtered_entities:
            span = doc.char_span(
                start, 
                end, 
                label=label,
                alignment_mode="contract"  # Präzisere Ausrichtung
            )
            if span:
                spans.append(span)
            else:
                print(f"⚠️ Ungültiger Span: '{text[start:end]}' ({start}-{end})")

        # Stufe 3: Endgültige Token-basierte Filterung
        spans = filter_overlapping_spans(spans)
        
        try:
            doc.ents = spans
            db.add(doc)
        except Exception as e:
            print(f"❌ Kritischer Fehler bei: '{text}'\n{'-'*40}")
            print(f"Entitäten: {filtered_entities}")
            print(f"Spans: {[(s.start_char, s.end_char, s.label_) for s in spans]}")
            print(f"Fehlerdetails: {str(e)}\n{'='*40}")
            
    return db

def train_ner(train_docs, labels, iterations=20):
    nlp = spacy.blank("de")
    
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    for label in labels:
        ner.add_label(label)

    optimizer = nlp.begin_training()

    # Create examples using the processed docs
    examples = []
    for doc in train_docs:
        # The reference doc has correct entities, predicted doc is tokenized
        predicted_doc = nlp.make_doc(doc.text)
        example = Example(predicted_doc, doc)
        examples.append(example)

    for itn in range(iterations):
        random.shuffle(examples)
        losses = {}
        batches = minibatch(examples, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            nlp.update(batch, sgd=optimizer, drop=0.2, losses=losses)
        print(f"Iteration {itn+1}/{iterations} - Losses: {losses}")

    return nlp



def train_model(TRAIN_DATA):
    db = create_training_data(TRAIN_DATA)
    db.to_disk(SPACY_TRAIN_DATA)
    print("create Training Data")
    
    nlp = spacy.blank("de")
    train_docs = list(db.get_docs(nlp.vocab))
    
    print("Train NER-Modell...")
    nlp_model = train_ner(train_docs, LABELS)
    print("Save Model...")
    nlp_model.to_disk(SPACY_MODEL)
    return nlp_model

def test_model(input=None, model=None):
    if model is None:
        model = spacy.load(SPACY_MODEL)
    doc = model(input)
    res = []
    for ent in doc.ents:
        res.append([ent.text, ent.label_])
    return res