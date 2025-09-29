"""
Helper functions to determine if ketogenic recipes are available in the search results.
"""
import json
import ast
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.evaluation.is_ketogen import is_ketogenic
from analysis_helper.load_dataset import get_file_path


def reduce_duplicates(ls):
    """Reduce duplicate recipes based on their
      IDs in a list of lists of recipe dicts."""
    items = []
    res = []
    try:
        for recipe_ls in ls:
            for recipe in recipe_ls:
                id = recipe.get("id")
                if id not in items:
                    res.append(is_ketogenic(protein_g=recipe.get("proteins"),
                                            carbs_g=recipe.get("carbohydrates"),
                                            fat_g=recipe.get("fat"),
                                            calories=recipe.get("calories")))
                    items.append(id)
    except Exception as exception: #pylint: disable=broad-except
        print(exception)
        return res
    return res


def ketogen_available(persona_id: int, query: str, model: ModelEnum, Path = None):
    """Check if ketogenic recipes are available in the search results 
    and if the assistant recommended a non-ketogenic recipe."""
    ls = []
    assistant = None
    file_path = get_file_path(Path=Path, query=query, persona_id=persona_id, model=model)
    if not file_path.exists():
        return 0
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # kaputte Zeilen überspringen
                if obj.get("role") == "Search_Results":
                    meta = obj.get("meta")
                    if type(meta) is not list and meta is not None:
                        try:
                            meta = ast.literal_eval(meta)
                        except: #pylint: disable=bare-except
                            print(meta) 
                    if meta is not None:
                        ls.append(meta)
                if obj.get("role") == "assistant":
                    content = obj.get("content")
                    if type(content) is not list:
                        content = ast.literal_eval(content)
                    recipe = content[0]
                    assistant = is_ketogenic(protein_g=recipe.get("proteins"),
                                             carbs_g=recipe.get("carbohydrates"),
                                             fat_g=recipe.get("fat"),
                                             calories=recipe.get("calories"))
            ls = reduce_duplicates(ls)
            if assistant is None or assistant is True:
                return None
            available = True if True in ls else False
            if assistant is False and available:
                return True
            return False

    except Exception as exception: #pylint: disable=broad-except
        print(exception)
        return None
    return None
