from elasticsearch import Elasticsearch


ELASTIC_URL = "http://172.17.0.1:9200"

INDEXES = ["works3", "authors"]

DEFAULT_SEARCH_FIELDS = ["abstract", "title"]
SEARCH_FIELDS = ["abstract", "title", "ngrams*","countries", "countries_hist", "language","type","publication_year","open_access.is_oa"]
SMALL_FIELDS = ["language", "type","open_access.is_oa"]

DISPLAYED_FIELDS = ["id", "title", "language", "countries", "countries_hist", "publication_year"]
CARD_FILTERS = ["topics"]
es = Elasticsearch(ELASTIC_URL)
