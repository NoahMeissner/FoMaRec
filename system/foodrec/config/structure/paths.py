#. 13.06.2025 @Noah Meissner

"""
This File handles Paths in the Project
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3] 
FOODREC = BASE_DIR / "foodrec"
CONFIG = FOODREC / "config"

# LLMs
LLMS_FOODREC = FOODREC / "llms"


#Dataset
DATASET_PATHS = CONFIG / "dataset"

ALL_RECIPE = DATASET_PATHS / "all_recipe"
DATASET_EVALUATION = DATASET_PATHS / "evaluation"

EMBEDDINGS = DATASET_PATHS / "ingredient_embeddings"

CONVERSATION = DATASET_PATHS / "conversation"

#Prompts 
PROMPTS = CONFIG / "prompts"
AGENT_PROMPTS = PROMPTS / "agent_prompt"
EVALUATION_PROMPTS = PROMPTS / "evaluation"