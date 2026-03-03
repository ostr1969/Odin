import os
import subprocess
import tempfile
import zipfile
# This script processes zip files in the specified folder, extracts text content from supported file types (PDF, DOC, DOCX) using Apache Tika, and updates the corresponding documents in Elasticsearch with the extracted content.
from elasticsearch import Elasticsearch, helpers
import requests
ES_INDEX = "libgen"
TIKA_URL = "http://localhost:9998/tika"

es = Elasticsearch("http://localhost:9200")
ZIP_FOLDER = "../Samples"
BATCH_SIZE = 500
actions = []
def extract_djvu_text(filepath):
    try:
        result = subprocess.run(
            ["djvutxt", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception:
        return None
def extract_with_tika(filepath):
    with open(filepath, "rb") as f:
        response = requests.put(
            TIKA_URL,
            data=f,
            headers={"Accept": "text/plain"}
        )
    if response.status_code == 200:
        return response.text
    return None

for zip_name in os.listdir(ZIP_FOLDER):
    if not zip_name.endswith(".zip"):
        continue
    print(f"Processing {zip_name}...")
    with zipfile.ZipFile(os.path.join(ZIP_FOLDER, zip_name), "r") as z:
        for member in z.namelist():
            file_hash = os.path.basename(member)

            # Get extension from ES (prefer using _id if hash is ID)
            try:
                doc = es.get(index=ES_INDEX, id=file_hash)
                ext = doc["_source"].get("Extension", "").lower()
            except:
                print(f"Document with ID {file_hash} not found in ES. Skipping.")
                continue

            if ext not in ["pdf", "doc", "docx","djvu","epub"]:
                continue

            # Extract to temp
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(z.read(member))
                tmp_path = tmp.name

            try:
                #print(f"Extracting {file_hash} with extension {ext}...")
                if ext == "djvu":
                    text = extract_djvu_text(tmp_path)
                else:
                    text = extract_with_tika(tmp_path)
                #print(text[:100])  # Print first 100 chars for verification
                if text:
                    actions.append({
                        "_op_type": "update",
                        "_index": ES_INDEX,
                        "_id": file_hash,
                        "doc": {"content": text}
                    })
                print(f"Processed {file_hash} with extension {ext}")
                if len(actions) >= BATCH_SIZE:
                    helpers.bulk(es, actions)
                    actions = []

            finally:
                os.remove(tmp_path)

# Flush remaining
if actions:
    helpers.bulk(es, actions)