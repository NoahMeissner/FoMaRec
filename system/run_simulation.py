"""
Script to run the simulation and create the dataset.
"""
from foodrec.evaluation.create_dataset import create_dataset
from foodrec.config.structure.dataset_enum import ModelEnum 

"""
You can choose between:
ModelEnum.Gemini  -> Gemini Flash 2.0
ModelEnum.Gemini_Pro -> Gemini Pro 2.5
ModelEnum.OpenAi -> GPT 5mini
None -> Only Search Engine

Biase Agent: False | True (System Biase)
Search Agent: False | True (Search Biase)
"""

try:
    df = create_dataset(model=ModelEnum.Gemini, biase_agent=False, biase_search=True)
except Exception as exception:
    for i in range(0,3):
        print("Error during dataset creation, retrying...")
    raise exception


