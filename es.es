get works3/_search?filter_path=*.*.*.countries
{"query": {"bool": {"must": [{"match": {"countries": "IL"}}, {"multi_match": {"query": "lazer", "fields": ["abstract", "title"]}}]}}}