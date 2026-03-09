from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
HOST="172.17.0.1"
ES_INDEX = "libgen"
TIKA_URL = "http://localhost:9998/tika"
model = SentenceTransformer("all-MiniLM-L6-v2",local_files_only=True)

es = Elasticsearch(f"http://{HOST}:9200")
ZIP_FOLDER = "../Samples"
BATCH_SIZE = 500
