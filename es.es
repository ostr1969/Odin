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