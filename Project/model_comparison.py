from train_ner import train_model, test_model
from load_annotation import load_dataset
from prompts import ingredients_extraction
from request_gemini import request
import pandas as pd
from DataLoader_Ingredients import DataLoader
dataset = load_dataset()
print(len(dataset))

#model = train_model(dataset)
test = test_model("3 el:kirschmarmelade")

#df_whole = pd.read_csv("Data/dataset.csv")
#loader_obj = DataLoader()
#train, test = loader_obj.get_set()




#prompt = ingredients_extraction.prompt_ingredients
#prompt = prompt.replace("$DATA$",test)

#print(request(prompt))
