from pathlib import Path

# Basisverzeichnis
'BASE_DIR = Path(__file__).resolve().parent.parent
'
# Datenverzeichnisse
DATA_DIR = BASE_DIR / "Data"
INGREDIENTS_DIR = DATA_DIR / "Ingredients"
MODELS = BASE_DIR/ "model"
TRAIN = BASE_DIR/"train"

# Models
SPACY_MODEL = MODELS/ "ingredients_ner_model"
BERT_MODEL = MODELS / "modern_bert/model.pt"
SPACY_TRAIN_DATA = TRAIN / "train.spacy"

#Datasets
RAW_SET = DATA_DIR/ "dataset.csv"

#Normalization
NORMALIZATION_DIR = DATA_DIR / "IngredientNormalization"
NOR_TRA = NORMALIZATION_DIR / "Training"
NOR_EVAL = NORMALIZATION_DIR / "Evaluation"

#NER
NER_EVAL  = INGREDIENTS_DIR / "Evaluation"
NER_TRA  = INGREDIENTS_DIR / "Training"
NER_PRE = INGREDIENTS_DIR / "preSafe"

#NOR
NOR_DIR = BASE_DIR / "normalizer"
NOR_LABEL = NOR_DIR / "normalizer_labels"
NOR_LABEL_UNITS = NOR_LABEL / "units.json"



