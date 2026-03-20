from config import es,FILES_DIR
import streamlit as st
from pathlib import Path
import os,shutil
import streamlit.components.v1 as components

#FILES_DIR = "files"  # local folder inside your app
def get_topics_dn(ids_dict:dict,index:str):
    ids=[topic["key"] for topic in ids_dict]
    topdict={}
    resd={}
    for t in ids_dict:
        topdict[t["key"]]=t["doc_count"]
    for id in ids:
        resp = es.search(
        index=index,
        body={
            "query": {
                "term": {"topics.id": id}
            },
            "_source": ["topics.id", "topics.display_name"],
            "size": 1
        }
        )
        for t in resp["hits"]["hits"][0]["_source"]["topics"]:
           if t["id"] in topdict:
                resd[t["id"]]=(t["display_name"],topdict[t["id"]]) 
    return resd
def get_concepts_dn(ids_dict:dict,index:str):
    ids=[concept["key"] for concept in ids_dict]
    
    conceptdict={}
    resd={}
    for t in ids_dict:
        conceptdict[t["key"]]=t["doc_count"]
    for id in ids:
        resp = es.search(
        index=index,
        body={
            "query": {
                "term": {"concepts.id": id}
            },
            "_source": ["concepts.id", "concepts.display_name"],
            "size": 1
        }
        )
        for t in resp["hits"]["hits"][0]["_source"]["concepts"]:
           if t["id"] in conceptdict:
                resd[t["id"]]=(t["display_name"],conceptdict[t["id"]]) 
    return resd
def check_es_alive():
    res=es.ping()
    if res:
        print("Connected to Elasticsearch")
        return True
    else:
        print("Failed to connect to Elasticsearch")
        return False
def build_query(filters):
    must = []

    for f in filters:
        field = f["field"]

        if field == "abstract+title":
            must.append({
                "query_string": {
                    "query": f["value"],
                    "fields": ["abstract", "title"]
                }
            })
        elif field == "abstract+title+content":
            must.append({
                "query_string": {
                    "query": f["value"],
                    "fields": ["abstract", "title", "content"]
                }
            }) 
        elif field == "title":
            must.append({
                "query_string": {
                    "query": f["value"],
                    "fields": [ "title"]
                }
            })                    
        elif field == "publication_year":
            rng = {}
            if f.get("from"):
                rng["gte"] = int(f["from"])
            if f.get("to"):
                rng["lte"] = int(f["to"])

            if rng:
                must.append({"range": {"publication_year": rng}})
        elif field == "ngrams*":
            must.append({
                "query_string": {
                    "query": f["value"],
                    "fields": ["ngrams*"]
                }
            })    
        elif field in ["language","type","topics.id","concepts.id"]:
            must.append({
                "terms": {
                    field: f["value"]
                }
            })        
        elif field == "id": 
              if "openalex" in f.get("value"):
                s=f.get("value")
              else:
                s="https://openalex.org/"+f.get("value")   
              must.append({"match": {field: s}})   
        else:
            if f.get("value"):
                must.append({"match": {field: f["value"]}})
    query= {"bool": {"must": must}}
    #print(query)
    return query   
def firstsearch(filters):
    
    q=build_query(filters)
    res = es.search(
            index=st.session_state.ind,
            track_total_hits=True,
            query=q,
            size=100,
            
            aggregations={
               
                    "topics": {
                        "terms": {
                            "field": "topics.id",
                            "size": 10
                            }
                    
                }, 
                     "concepts": {
                        "terms": {
                            "field": "concepts.id",
                            "size": 10
                            }
                    
                }, 
                    "types":{ "terms": { "field": "type", "size": 10 }},
                    "language":{ "terms": { "field": "language", "size": 5 }}
            }
        )
    #print(res["hits"]["total"]["value"])
    return res

def mybutton(label, key=None, bgcolor=None, fgcolor=None, reversed=False, padding=None, **kwargs):
    if key is None:
        raise ValueError("You must provide a unique key")

    styles = []
    

    if bgcolor:
        styles.append(f"background-color: {bgcolor};")

    if fgcolor:
        styles.append(f"color: {fgcolor};")
    if reversed:
        styles.append(f"background-color: black; color: white;")
    if padding:
        styles.append(f"padding: {padding};")  # e.g. "10px 20px"

    if styles:
        style_str = " ".join(styles)
       

        st.markdown(f"""
        <style>
        div.st-key-{key} button {{
            {style_str}
        }}
        div.st-key-{key} button:hover {{
            filter: brightness(0.9);
        }}
        </style>
        """, unsafe_allow_html=True)

    return st.button(label, key=key, **kwargs) 
def download(id):
        
        id1=id.replace('https://openalex.org/','')
        path=es.get(index=st.session_state.ind, id=id1)["_source"].get("path","")
        path=r"/workspace/Aftabi.pdf"
        #st.write(f"File path: {path}, id: {id}")

        # --- PDF: open directly (no copy) ---
  
        local_url = f"http://localhost:8000/{path}"

        filename = Path(path).name
        ext = Path(path).suffix  

        # --- Non-PDF: copy + load ---
        local_path = os.path.join(FILES_DIR, id1+ext)
        #print(FILES_DIR,id1+ext)

        # Copy only once
        if not os.path.exists(local_path):
            with st.spinner("Copying file..."):
                shutil.copyfile(path, local_path)
        #open file server on the root of the files by "python -m http.server 8000"
        # st.markdown(
        #         f'<a href="http://localhost:8000/{id1+ext}" target="_blank">📄 Open PDF</a>',
        #         unsafe_allow_html=True
        #     )
        
        components.html(f"""
        <script>
           
            // You can also open a URL in a new tab
            window.open("http://localhost:8000/{id1+ext}", "_blank");
        </script>
    """, height=0, width=0)
        #print("downloaded:"+f"http://localhost:8000/{id1+ext}")