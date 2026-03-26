get works3/_search?filter_path=agg*
{"query": {"bool": {"must": [{"query_string": 
        {"query": "lazer", "fields": ["abstract"]}} 
        ]}}, "size": 1000,
        "aggs": {
                    "topics": {
                       "terms": {
                            "field": "topics.id",
                            "size": 10
      }
                            }
                }}
get works3/_search?filter_path=agg*
{"size": 100, "aggs": {"values": {"terms": {"field": "open_access.is_oa", "size": 50}}}}

PUT works3/_mapping
{"properties":{"open_access":{"properties":{"is_oa":{"type":"boolean"}}}}}

POST works3/_update_by_query
{
  "script": {
    "source": "ctx._source.open_access.is_oa = ctx._source.open_access.is_oa ",
    "lang": "painless"
  }
}
get works3/_search?filter_path=agg*
{
    "size": 100,
    "aggs": {
        "values": {
            "terms": {
                "field": "type",
                "size": 50
            }
        }
    }
}
get libgen/_search
{
    "size": 100,
    "query": {
        "bool": {
            "must": [
                {
                    "term": {
                        "Extension.keyword": "mobi"
                    }
                }
            ]
        }
    }
}
get works3/_search?filter_path=*.*.*.title,*.*.*.publ*
{
    "query": {
        "query_string": {
            "query": "Pouchers Perfumes, Cosmetics and Soaps",
            "fields": [
                "title"
            ],
            "fuzziness": "AUTO",
        "minimum_should_match": "70%"
        }
    }
}

get works3/_search?filter_path=*
{
    "query": {
        "bool": {
            "must": [
                {
                    "query_string": {
                        "query": "Training strategies",
                        "fields": [
                            "abstract",
                            "title"
                        ]
                    }
                }
            ]
        }
    },
    "size": 100,
    "track_total_hits": true,
    "aggs":{
               
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
}

POST libgen/_update/874611_d5c5af05d51c83da3a4cb833d5e830f7
{
  "doc": {
    "content": "Alice in Wonderland "
  }
}
get works3/_search?filter_path=*.*.*.title,*.*._score,*.*._explanation
{
    "size": 1,
    "explain": true,
    "query": {
        "function_score": {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "term": {
                                "language": "en"
                            }
                        }
                    ],
                    "should": [
                        {
                            "match_phrase": {
                                "title": {
                                    "query": "Magnetic Domains: The Analysis of Magnetic Microstructures",
                                    "slop": 2,
                                    "boost": 5
                                }
                            }
                        },
                        {
                            "match": {
                                "title": {
                                    "query": "Magnetic Domains: The Analysis of Magnetic Microstructures",
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