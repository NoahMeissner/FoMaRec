# Noah Meissner 16.07.2025

database_structure = {
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },

      "title": {
      "type": "text",
      "analyzer": "standard",
      "fields": {
        "raw": {
          "type": "keyword",
          "ignore_above": 200
        }
      }
    },

      "rate_average": { "type": "float" },
      
 
      # Enhanced ingredients field for better searchability
      "ingredients": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword",
            "normalizer": "lowercase_normalizer"
          },
          "suggest": {
            "type": "completion"
          }
        },
        "meta": {
          "description": "Supports exclusion queries"
        }
      },

      # Enhanced tutorial field
      "tutorial": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "raw": { "type": "keyword" }
        }
      },


      "cooking_time": {
        "type": "integer",
        "meta": {
          "description": "Cooking time in minutes"
        }
      },


      # Nutritional information
      "kcal": { "type": "float" },
      "protein": { "type": "float" },
      "carbohydrates": { "type": "float" },
      "fat": { "type": "float" },

      "recipe_href": {
        "type": "keyword",
        "index": False
      },

      # Enhanced cuisine field
      "cuisine": {
        "type": "keyword",
        "fields": {
          "text": {
            "type": "text",
            "analyzer": "standard"
          }
        }
      },

      "embeddings": {
        "type": "dense_vector",
        "dims": 768,  
        "index": True,
        "similarity": "cosine",
        "index_options": {
          "type": "hnsw",
          "m": 16,
          "ef_construction": 100
        }
      }

      
    }
  },
  
  # Add settings for better text analysis
  "settings": {
    "analysis": {
      "normalizer": {
        "lowercase_normalizer": {
          "type": "custom",
          "filter": ["lowercase", "asciifolding"]
        }
      },
      "analyzer": {
        "ingredient_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding", "stop"]
        }
      }
    },
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 1
    }
  }
}