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
            "query": "Poucher"s Perfumes, Cosmetics and Soaps",
            "fields": [
                "title"
            ],
            "fuzziness": "AUTO",
        "minimum_should_match": "70%"
        }
    }
}

get libgen/_search?filter_path=*.*.*.Title,*.*.*.publ*
{
    "query": {
        "match": {
            "Title": "magnetic"
        }
    }
}

POST libgen/_update/874611_d5c5af05d51c83da3a4cb833d5e830f7
{
  "doc": {
    "content": "Alice in Wonderland "
  }
}
get works3/_search?filter_path=*.*.*.title,*.*._score,*.*._explanation&search_type=dfs_query_then_fetch
{
    "size": 2,
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
                    "must_not": [
                        {
                            "term": {
                                "type": "article"
                            }
                        }
                    ],
                    "should": [
                        {
                            "match_phrase": {
                                "title": {
                                    "query": "Neuroscience",
                                    "slop": 2,
                                    "boost": 5
                                }
                            }
                        },
                        {
                            "match": {
                                "title": {
                                    "query": "Neuroscience",
                                    "operator": "and",
                                    "boost": 2
                                }
                            }
                        },
                        {
                            "match": {
                                "title": {
                                    "query": "Neuroscience",
                                    "fuzziness": "AUTO",
                                    "minimum_should_match": "70%",
                                    "boost": 1
                                }
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            "boost_mode": "multiply",
            "score_mode": "multiply",
            "functions": [
                {
                    "gauss": {
                        "publication_year": {
                            "origin": "2004",
                            "scale": 1,
                            "offset": 0,
                            "decay": 0.8
                        }
                    }
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
          "weight": 0.9
        }
            ]
        }
    }
}