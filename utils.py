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
    #print(resd)
    
    return resd