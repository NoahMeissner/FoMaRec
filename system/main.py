# 13.06.2025 @Noah Meissner

"""
Goal of this script is the intialisation of the Project
"""
from foodrec.utils.data_preperation.check_elastic import check_Elastic
#check_Elastic(biase_search=False)

from foodrec.tools.search import Search
from foodrec.config.structure.dataset_enum import DatasetEnum
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
search = Search(es_client=es, dataset_name=DatasetEnum.ALL_RECIPE)
a = search.search("I want sth with pork", pretty_print=True)