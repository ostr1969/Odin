import os
import zipfile
import tempfile
from elasticsearch import Elasticsearch
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
import subprocess

es = Elasticsearch("http://localhost:9200")

INDEX = "libgen"


def get_extension_from_es(file_hash):
    res = es.search(
        index=INDEX,
        query={"term": {"MD5": file_hash}},
        size=1
    )
    hits = res["hits"]["hits"]
    if not hits:
        return None
    return hits[0]["_source"].get("extension")


def extract_text_from_file(filepath, ext):
    ext = ext.lower()

    if ext == "pdf":
        return extract_pdf_text(filepath)

    elif ext == "docx":
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])

    elif ext == "doc":
        result = subprocess.run(
            ["antiword", filepath],
            capture_output=True,
            text=True
        )
        return result.stdout

    return None