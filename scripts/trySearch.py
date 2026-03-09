from elasticsearch import Elasticsearch
from difflib import SequenceMatcher
from rapidfuzz import fuzz
#matching title from libjen mysql db to openalex so that 
# we can use hushinjest to insert text and attach the pdf
HOST="172.17.0.1"

es = Elasticsearch(f"http://{HOST}:9200")
def semSearch(query):
  model=None
  query_embedding = model.encode(
      query,
      normalize_embeddings=True
  ).tolist()

  search_body = {
    "size": 10,
    "query": {
      "bool": {
        "should": [
          {
            "query_string": {
              "query": query,"fields": ["content"]
            }
          },
          {
            "knn": {
              "field": "embedding",
              "query_vector": query_embedding,
              "k": 50,
              "num_candidates": 200
            }
          }
        ]
      }
    }
  }

  res = es.search(index="libgen_chunks", body=search_body)

  for hit in res["hits"]["hits"]:
      print(hit["_score"], hit["_id"])
      print(hit["_source"]["content"][:100])
      print("-----")
def closestTitle(query,year,lang):
    #print(f"Searching for {query} ({year}, {lang})")
    body={
    "size":1,
    "query": {
      "function_score": {
        "query": {
          "bool": {
            "filter": [
              {
                "term": {
                  "language": lang
                }
              }
            ],
            "must_not":[{
                "term": {
                  "type": "article1"
                }
              }],
            "should": [
              {
                "match_phrase": {
                  "title": {
                    "query": query,
                    "slop": 2,
                    "boost": 5
                  }
                }
              },
              {
                "match": {
                  "title": {
                    "query": query,
                    "operator": "and",
                    "boost": 2
                  }
                }
              }
            ],
            "minimum_should_match": 1
          }
        },       
        "boost_mode": "multiply",
        "score_mode": "multiply"
      }
    }
  }  
    
    fuz=         {
                "match": {
                  "title": {
                    "query": query,
                    "fuzziness": "AUTO",
                    "minimum_should_match": "70%",
                    "boost": 1
                  }
                }
              }
    #year=0  
    if year!=0:
      body["query"]["function_score"]["functions"] =  [
          {
            "linear": {
              "publication_year": {
                "origin": year,
                "scale": 1,
                "offset": 0,
                "decay": 0.8,
                
              }
            },
            "weight": 1
          },
          {
          "filter": {
            "bool": {
              "must_not": {
                "exists": {
                  "field": "publication_year"
                }
              }
            }
          },
          "weight": 0.99
        }
        ]
      
    #print(body) 
    
    res = es.search(index="works3", body=body)  
    if len(res["hits"]["hits"])==0:
        print("---None---")
        
        return
    for hit in res["hits"]["hits"]:
      #ratio=SequenceMatcher(None, query, hit["_source"]["title"]).ratio()
      ratio=fuzz.ratio(query, hit["_source"]["title"])/100
      print(f"OA:{hit["_source"].get("publication_year","")}:{hit["_source"]["title"]} ({hit["_source"]["type"]},{ratio:.2f})")
      #print(f"OA:{hit["_source"].get("publication_year","")}:{hit["_score"]}:{hit["_source"]["title"]} ({hit["_source"]["type"]})")
    print("-----")
    
if __name__ == "__main__":
    # semSearch(query)
    n=60
    response=es.search(index="libgen", query= {"match": {"Title": "magnetic Domains"}},size=n)
    for hit in response["hits"]["hits"]: 
        year=hit["_source"].get('Year', 2000) or 2000  
        if hit["_source"].get('Language', '')!="English":
          continue     
        print(f"LG:{hit["_source"].get('Year', 0)}:{hit["_source"]["Title"]}")
        
        try:
          closestTitle(hit["_source"]["Title"],year,"en")  
        except Exception as e:
          print("Error:", e)    