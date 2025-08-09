# Noah Meissner 12.07.2025

"""
This class is responsible for the Request to the Elastic Database
"""

"""
Structure:
Data
{'time': [0, 30], 'difficulty': 'easy', 'cuisine': None, 'calories': None, 'include': ['garlic'], 'avoid': None}
request -> str
request_embedding -> np.array
"""

def request_elastic(request_embedding, data, es_client, index_name="database"):
    must_clauses = []
    must_not_clauses = []
    filter_clauses = []

    # Ingredients (include)
    if data.get("include"):
        for ingredient in data["include"]:
            must_clauses.append({
                "match": {
                    "ingredients": ingredient
                }
            })

    # Ingredients (avoid)
    if data.get("avoid"):
        for ingredient in data["avoid"]:
            must_not_clauses.append({
                "match": {
                    "ingredients": ingredient
                }
            })

    # Cuisine (multi-label match)
    if data.get("cuisine"):
        filter_clauses.append({
            "terms": {
                "cuisine": data["cuisine"]
            }
        })

    # Cooking Time (range)
    if data.get("time"):
        print("hiers")
        filter_clauses.append({
            "range": {
                "cooking_time": {
                    "gte": data["time"][0],
                    "lte": data["time"][1]
                }
            }
        })

    # Calories (range)
    if data.get("calories"):
        filter_clauses.append({
            "range": {
                "calories": {
                    "gte": data["calories"][0],
                    "lte": data["calories"][1]
                }
            }
        })

    # Optional: Frage → Embedding-Suche
    embedding = request_embedding

    # Query ohne Embedding
    if embedding is None:
        query = {
            "bool": {
                "must": must_clauses,
                "must_not": must_not_clauses,
                "filter": filter_clauses
            }
        }
    else:
        query = {
            "script_score": {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "must_not": must_not_clauses,
                        "filter": filter_clauses
                    }
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embeddings') + 1.0",
                    "params": {
                        "query_vector": embedding
                    }
                }
            }
        }
    #print(query)
    # Elasticsearch Request
    response = es_client.search(index=index_name, body={"query": query})
    return response
