from config import es,FILES_DIR

from pathlib import Path
import os,shutil


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
        print(field)
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
def firstsearch(filters,ind):
    
    q=build_query(filters)
    #print(q)
    res = es.search(
            index=ind,
            track_total_hits=True,
            query=q,
            size=100
            
            
        )
    #print(res["hits"]["total"]["value"])
    return res

def aggsearch(filters,ind,aggby):
    
    q=build_query(filters)
    
    res = es.search(
            index=ind,            
            query=q,
            size=0,
            #topics:topics.id
            #concepts:concepts.id
            #types:type
            #language:language
            aggregations={
               
                    "somename": {
                        "terms": {
                            "field": aggby,
                            "size": 10
                            }
                    
                }
            }
        )
    #print(res["hits"]["total"]["value"])
    return res

def get_filters(session):
    #print(session)
    filters=[{"field":session["field"],"value":session["query"]}]
    if session["filters"].get("dchoice") == "0":
        filters.append({"field":"publication_year","from":2025,"to":3000})
    elif session["filters"].get("dchoice") == "1":
        filters.append({"field":"publication_year","from":2020,"to":3000})
    elif session["filters"].get("dchoice") == "custom":       
        filters.append({"field":"publication_year","from":session["filters"].get("from_year"),
                        "to":session["filters"].get("to_year")})
    if session["filters"].get("type_filters"):
        filters.append({"field":"type","value":session["filters"].get("type_filters")}) 
    if session["filters"].get("topic_filters"):
        filters.append({"field":"topics.id","value":session["filters"].get("topic_filters")}) 
    if session["filters"].get("concept_filters"):
        filters.append({"field":"concepts.id","value":session["filters"].get("concept_filters")})             
    if session["filters"].get("language_filters"):
        filters.append({"field":"language","value":session["filters"].get("language_filters")}) 
    if session.get("oa_filter"):
        filters.append({"field":"primary_location.is_oa","value":session["filters"].get("oa_filter")}) 
    return filters    
