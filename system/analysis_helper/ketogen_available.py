from foodrec.config.structure.dataset_enum import ModelEnum 
import json
import ast
from foodrec.evaluation.is_ketogen import is_ketogenic, calc_keto_ratio


def reduce_duplicates(ls):
    items = []
    res = []
    try:
        for recipe_ls in ls:
            for recipe in recipe_ls:
                id = recipe.get("id")
                if id not in items:
                    res.append(is_ketogenic(protein_g=recipe.get("proteins"),carbs_g=recipe.get("carbohydrates"), fat_g=recipe.get("fat"), calories=recipe.get("calories")))
                    items.append(id)
    except Exception as e:
        return res
    return res


def ketogen_available(persona_id: int, query: str, model: ModelEnum, Path = None):
    query_stempt = query.replace(" ", "_").lower()
    id = f"{persona_id}_{query_stempt}_{model.name}"
    ls = []
    assistant = None
    filepath = Path / f"{id}.jsonl"
    if not filepath.exists():
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            num = 0
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
                        except:
                            print(meta)
                    if meta is not None:
                        ls.append(meta)
                if obj.get("role") == "assistant":
                    content = obj.get("content")
                    if type(content) is not list:
                        content = ast.literal_eval(content)
                    recipe = content[0]
                    assistant = is_ketogenic(protein_g=recipe.get("proteins"),carbs_g=recipe.get("carbohydrates"), fat_g=recipe.get("fat"), calories=recipe.get("calories"))
            ls = reduce_duplicates(ls)
            if assistant == None or assistant == True:
                return None
            available = True if True in ls else False
            if assistant == False and available:
                return True
            else:
                return False

    except Exception as e:
        return None
    return None
