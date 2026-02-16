get works3/_search?filter_path=*.*.*.ngram*
{"query": {"bool": {"must": [{"query_string": 
        {"query": "lazer", "fields": ["abstract"]}} ,
        {"match": {"ngram*": "robotics"}}]}}, "size": 100}