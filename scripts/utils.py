import os
import shutil
import subprocess

import mobi,requests
import html2text
from __init__ import TIKA_URL

def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
def mobi_to_text(mobi_filepath):
    # 1. Extract the content from the MOBI file
    # mobi.extract creates a temporary directory and returns paths to the dir and the extracted file
    tempdir, filepath = mobi.extract(mobi_filepath)
    
    try:
        # 2. Read the extracted file content (usually HTML)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 3. Convert the HTML content to plain text
        # The html2text library handles the conversion from HTML to a readable text format
        text_content = html2text.html2text(content)
        
        return text_content

    finally:
        # 4. Clean up the temporary directory created by mobi.extract
        if tempdir and os.path.exists(tempdir):
            shutil.rmtree(tempdir)
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