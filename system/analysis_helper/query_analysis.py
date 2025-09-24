"""
This module provides functions to analyze and evaluate recipe recommendations"""
import os
import math
import ast
import pandas as pd
import numpy as np
import json
from typing import List
from analysis_helper.load_dataset import get_file_path
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.config.structure.paths import DATASET_PATHS
from foodrec.tools.ingredient_normalizer import IngredientNormalisation
from foodrec.config.structure.dataset_enum import DatasetEnum
from foodrec.utils.search.request_information_extraction import extract_information

def translate_cuisine(ls):
    """Translate various cuisine inputs to a standardized set."""
    mapping = {
        "europe": "central_europe",
        "middle_east": "middle_east",
        "asia": "asia",
        "latin": "latin_america",
        "north american": "north_america",
        "0": None,     
        "nan": None,    
        "none": None
    }

    if ls is None:
        return None
    try:
        if isinstance(ls, float) and math.isnan(ls):
            return None
    except Exception:
        pass

    if ls == 0:
        return None

    if not isinstance(ls, (list, tuple, set)):
        ls = [ls]

    res = []
    for obj in ls:
        # normalize each token to a lowercase string
        key = str(obj).strip().lower()
        canon = mapping.get(key, key)
        if canon:
            res.append(canon)

    return res or []

def ingredient_normalisation(normalizer, ing):
    """Normalize a list of ingredient strings using the provided normalizer."""
    res = []
    for ingredient in ing:
        try:
            res.append(normalizer.normalize(ingredient)[0])
        except: continue
    return res

def calc_other_recommendation_parameters(query_set, Path, model, n=1, Search_engine=False):
    """Calculate various recommendation parameters such 
    as ingredient inclusion, avoidance, and cuisine match."""
    def prepare_gt():
        path_gt = DATASET_PATHS / "Recommender_truth.csv"
        if not os.path.exists(path_gt):
            annotate = pd.read_csv(DATASET_PATHS / "zw_personas.csv", delimiter=",")
            annotate["Gemini"] = annotate["query"].apply(extract_information)
            annotate.to_csv(path_gt, index=False)
        else:
            annotate = pd.read_csv(path_gt)

        normalizer = IngredientNormalisation(DatasetEnum.ALL_RECIPE)
        dataset = annotate[["Gemini"]].copy()
        dataset["Gemini"] = dataset["Gemini"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

        fields = ["time", "ingredients_included", "ingredients_avoid", "cuisine", "calories"]
        for field in fields:
            dataset[f"{field}"] = dataset["Gemini"].apply(
                lambda d: d.get(field) if isinstance(d, dict) else None)
        dataset[f"cuisine"] = dataset[f"cuisine"].apply(
            lambda d: d if (len(d)<=2) else []
        )
        dataset[f"cuisine"] = dataset[f"cuisine"].apply(
            lambda d: translate_cuisine(d)
        )
        dataset["ingredients_included"] = dataset["ingredients_included"].apply(
            lambda d: ingredient_normalisation(normalizer, d)
            if d is not None or d == []
            else []
        )
        dataset["ingredients_avoid"] =dataset["ingredients_avoid"].apply(
            lambda d: ingredient_normalisation(normalizer, d)
            if d is not None or d == []
            else []
        )

        return dataset

    def get_recipes(persona_id: int, query: str, model: ModelEnum, Path = None):
        """Get the top-n recommended recipes from the search results."""
        filepath = get_file_path(Path=Path, query=query, persona_id=persona_id, model=model)
        if filepath is None:
            return 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:

                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # kaputte Zeilen überspringen
                    if obj.get("role") == "assistant":
                        content = obj["content"]
                        return content
        except:
            return None
        return None

    def get_search_engine(queries: List[str], Path = None):
        """Get recipes from a search engine JSON file."""
        filepath = Path
        recipes = []
        if not filepath.exists():
            print("error")
            return 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                obj = json.loads(f.read())
                recipes = [obj.get(query) for query in queries]
                return recipes
        except Exception as e:
            print(e)
            return None

    def analyse_cuisine(gt, recipe_list):
        """Analyze the cuisine match between ground truth and recommended recipes."""
        ls = []
        for index, row in gt.iterrows():
            try:
                recipe_query_list = recipe_list[index]
                recipe = (recipe_query_list[0]
                          if recipe_query_list is not None and len(recipe_query_list)>=1
                          else None
                )
                if recipe is not None:
                    cuisine_recipe = recipe["cuisine"]
                    cuisine = row["cuisine"]
                    if cuisine is not None and cuisine != []:
                        if cuisine_recipe in cuisine:
                            ls.append(True)
                        else:
                            ls.append(False)
            except:
                continue
        return np.mean(ls)

    def analyse_ingredient_include(gt, recipe_list, id="ingredients_included"):
        """Analyze the inclusion of desired ingredients in the recommended recipes."""
        ls = []
        for index, row in gt.reset_index(drop=True).iterrows():
            try:
                recipe_query_list = recipe_list[index] if index < len(recipe_list) else None
                recipe = (recipe_query_list[0]
                        if recipe_query_list and len(recipe_query_list) >= 1
                        else None)
                if not recipe:
                    continue

                recipe_ings_raw = recipe.get("ingredients") or []
                recipe_ings = [
                    str(x).replace("'", "").lower().strip()
                    for x in recipe_ings_raw if x is not None
                ]

                include = row.get(id) or []
                if isinstance(include, str):
                    include = [include]

                for ing in include:
                    if not ing:
                        continue
                    ing_norm = str(ing).replace("'", "").lower().strip()
                    found = any(ing_norm in base for base in recipe_ings)
                    ls.append(found)
            except Exception as e:
                print(f"Row {index}: {e}")
                continue
        return np.mean(ls)

    gt = prepare_gt()
    if Search_engine:
        recipes = get_search_engine(list(query_set['query']), Path=Path)
    else:
        recipes = [
            get_recipes(row['id'], row['query'], model=model, Path=Path)
            for _, row in query_set.iterrows()
        ]
    avoid = 1 - analyse_ingredient_include(gt, recipes, id ="ingredients_avoid")
    like = analyse_ingredient_include(gt, recipes)
    cuisine = analyse_cuisine(gt, recipes)
    overall = (avoid+like+cuisine)/3
    print(f"Like {like}")
    print(f" Avoid {avoid}")
    print(f"Cuisine {cuisine}")
    print(f"Overall{(overall)}")
