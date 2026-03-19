from config import es
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
        elif field == "id": 
              if "openalex" in f.get("value"):
                s=f.get("value")
              else:
                s="https://openalex.org/"+f.get("value")   
              must.append({"match": {field: s}})   
        else:
            if f.get("value"):
                must.append({"match": {field: f["value"]}})
    query={"query": {"bool": {"must": must}},"size":100}
    #print(query)
    return query    