from config import es
import streamlit as st
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
        elif field == "types":
            must.append({
                "terms": {
                    "type": f["value"]
                }
            })  
        elif field == "language":
            must.append({
                "terms": {
                    "language": f["value"]
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
