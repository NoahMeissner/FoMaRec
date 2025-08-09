# Noah Meissner 16.07.2025

"""
    This script loads the self trained script from Hugging face and classifies the overhanded ingredients
"""
from huggingface_hub import hf_hub_download
import joblib
from foodrec.config.structure.dataset_enum import DatasetEnum

class CuisineClassifier:

    def __init__(self, dataset=None):
        print("🚀 Initializing CuisineClassifier...")

        if dataset is None:
            base_path = "model"
        elif dataset == DatasetEnum.ALL_RECIPE:
            base_path = "model/all_recipe"
        elif dataset == DatasetEnum.KOCHBAR:
            base_path = "model/kochbar"
        else:
            raise ValueError(f"❌ Unsupported dataset: {dataset}")

        components = ["cuisine_classifier", "vectorizer", "label_encoder"]
        paths = {}

        print("📡 Downloading files from Hugging Face Hub...")
        for name in components:
            print(f"⬇️ Downloading {name}.joblib ...")
            try:
                paths[name] = hf_hub_download(
                    repo_id="NoahMeissner/CuisineClassifier", 
                    filename=f"{base_path}/{name}.joblib"
                )
                print(f"✅ {name} downloaded.")
            except Exception as e:
                print(f"❌ Failed to download {name}: {e}")
                raise

        print("📦 Loading model components with joblib...")
        try:
            self.model = joblib.load(paths["cuisine_classifier"])
            print("✅ Model loaded.")
            self.vectorizer = joblib.load(paths["vectorizer"])
            print("✅ Vectorizer loaded.")
            self.label_encoder = joblib.load(paths["label_encoder"])
            print("✅ Label encoder loaded.")
        except Exception as e:
            print(f"❌ Failed to load components: {e}")
            raise

        print("🎉 All components loaded successfully.")

    def classify(self, text_input):
        data = " ".join(text_input)
        X_input = self.vectorizer.transform([data])
        predicted_class = self.model.predict(X_input)
        predicted_label = self.label_encoder.inverse_transform(predicted_class)
        return predicted_label
