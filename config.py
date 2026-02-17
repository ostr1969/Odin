from elasticsearch import Elasticsearch
ELASTIC_URL = "http://localhost:9200"

INDEXES = ["works3", "authors"]

DEFAULT_SEARCH_FIELDS = ["abstract", "title"]
SEARCH_FIELDS = ["abstract", "title", "ngrams*","countries", "countries_hist", "language","type","publication_year"]
SMALL_FIELDS = ["language", "type"]

DISPLAYED_FIELDS = ["id", "title", "language", "countries", "countries_hist", "publication_year"]
CARD_FILTERS = ["topics"]
es = Elasticsearch(ELASTIC_URL)