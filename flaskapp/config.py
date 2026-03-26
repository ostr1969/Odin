from elasticsearch import Elasticsearch


ELASTIC_URL = "http://172.17.0.1:9200"
OPEN_FILE_TYPES = ["pdf", "html", "xml", "json"]
INDEXES = ["works3", "authors3"]

FILES_DIR = "files"  # local folder inside your app

DEFAULT_SEARCH_FIELDS = ["abstract", "title"]
SEARCH_FIELDS = ["abstract", "title", "ngrams*","countries", "countries_hist", "language","type","publication_year","open_access.is_oa","id"]
SMALL_FIELDS = ["language", "type","open_access.is_oa"]

DISPLAYED_FIELDS = ["icon","id", "title", "language", "countries", "publication_year"]
CARD_FILTERS = ["topics"]
OPEN_FILE_TYPES=["pdf","txt"]
es = Elasticsearch(ELASTIC_URL)
