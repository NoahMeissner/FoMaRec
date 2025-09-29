# Noah Meissner 16.07.2025

"""
This class is responsible for the Set Up the Elastic Search Database
Following data categories:
- id
- title
- rating
- views
- rate_average
- person number
- ingredients(normalized)
- tutorial
- difficulty
- cooking time
- price category
- kcal
- protein
- carbohydrates
- fat
- recipe_href
- cuisine
- embeddings
- feature embeddings
"""
from foodrec.config.elastic.setup import database_structure


class SetUpElastic:

    def connect_elastic(self, es):
        try:
            es.info()
            if es.ping():
                print("Connection Succesful!")
                return es
            else:
                print("Connection Refused.❗️❗️")
        except Exception as e:
            print(e)

    def delete_database(self):
        if self.es.indices.exists(index=self.index_name):
            response = self.es.indices.delete(index=self.index_name, ignore_unavailable=True)
            if response.get("acknowledged"):
                print(f"Index '{self.index_name}' successfully deleted.")
            else:
                print(f"Deletion of index '{self.index_name}' not acknowledged.")

    def setUp(self):
        try:
            if self.new:
                self.delete_database()
            if self.es.indices.exists(index=self.index_name) and not self.new:
                return False
            self.es.indices.create(index=self.index_name, body=database_structure, wait_for_active_shards=1)
            return True
        except Exception as e:
            print(e)
            return None
        
    def __init__(self, es_client, index_name = "Database", new = False):
        self.es = self.connect_elastic(es_client)
        self.index_name = index_name
        self.new = new



    