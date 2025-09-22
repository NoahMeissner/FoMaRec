# Noah Meissner 16.07.2025

"""
    This script loads the self trained script from Hugging face and classifies the overhanded ingredients
"""
from huggingface_hub import hf_hub_download
import joblib

class CuisineClassifier:

    def __init__(self, dataset=None):
        print("🚀 Initializing CuisineClassifier...")


        components = ["cuisine_pipeline", "label_encoder"]
        paths = {}

        print("📡 Downloading files from Hugging Face Hub...")
        for name in components:
            print(f"⬇️ Downloading {name}.joblib ...")
            try:
                paths[name] = hf_hub_download(
                    repo_id="NoahMeissner/CuisineClassifier", 
                    filename=f"region_classifier/{name}.joblib"
                )
                print(f"✅ {name} downloaded.")
            except Exception as e:
                print(f"❌ Failed to download {name}: {e}")
                raise

        print("📦 Loading model components with joblib...")
        try:
            self.model = joblib.load(paths["cuisine_pipeline"])
            print("✅ Model loaded.")
            self.label_encoder = joblib.load(paths["label_encoder"])
            print("✅ Label encoder loaded.")
        except Exception as e:
            print(f"❌ Failed to load components: {e}")
            raise

        print("🎉 All components loaded successfully.")

    def classify(self, text_input):
        data = " ".join(text_input)
        predicted_class = self.model.predict([data])
        predicted_label = self.label_encoder.inverse_transform(predicted_class)
        return predicted_label
