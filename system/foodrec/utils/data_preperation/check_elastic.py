# Noah Meissner 15.08.2025

from foodrec.utils.elastic_search.elastic_manager import IndexElastic
from foodrec.config.structure.dataset_enum import DatasetEnum
from elasticsearch import Elasticsearch

def check_Elastic(biase_search:bool=False):
    es = Elasticsearch("http://localhost:9200")
    if not es.indices.exists(index='database'):
        IE = IndexElastic(dataset_name=DatasetEnum.ALL_RECIPE)
        IE.index_data(new=True, biase=biase_search)
