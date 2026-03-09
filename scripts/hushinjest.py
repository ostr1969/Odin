import os

import tempfile
import zipfile
from utils import chunk_text, mobi_to_text,extract_djvu_text,extract_with_tika
from __init__ import es, model, ES_INDEX,  BATCH_SIZE, ZIP_FOLDER


# This script processes zip files in the specified folder, 
# extracts text content from supported file types (PDF, DOC, DOCX) using Apache Tika, 
# and updates the corresponding documents in Elasticsearch with the extracted content.
from elasticsearch import  helpers


actions = []

def index_document(doc_id, text):
    chunks = chunk_text(text)

    embeddings = model.encode(
        chunks,
        show_progress_bar=False,
        normalize_embeddings=True
    )

    actions1 = []

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        actions1.append({
            "_index": "libgen_chunks",
            "_id": f"{doc_id}_{i}",
            "_source": {
                "doc_id": doc_id,
                "chunk_id": i,
                "content": chunk,
                "embedding": emb.tolist()
            }
        })
        
    helpers.bulk(es, actions1)
    print(f"Indexed {len(actions1)} chunks")




if __name__ == "__main__":
    

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

                if ext not in ["pdf", "doc", "docx","djvu","epub","mobi"]:
                    continue

                # Extract to temp
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(z.read(member))
                    tmp_path = tmp.name

                try:
                    #print(f"Extracting {file_hash} with extension {ext}...")
                    if ext == "djvu":
                        text = extract_djvu_text(tmp_path)
                    elif ext == "mobi":
                        text = mobi_to_text(tmp_path)
                    else:
                        text = extract_with_tika(tmp_path)
                    #print(text[:100])  # Print first 100 chars for verification
                    if text:
                        actions.append({
                            "_op_type": "update",
                            "_index": ES_INDEX,
                            "_id": file_hash,
                            "doc": {"chunked": True}
                        })
                        index_document(file_hash, text)
                    print(f"Processed {file_hash} with extension {ext}")
                    if len(actions) >= BATCH_SIZE:
                        helpers.bulk(es, actions)
                        actions = []

                finally:
                    os.remove(tmp_path)

    # Flush remaining
    if actions:
        helpers.bulk(es, actions)