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
get libgen/_search?filter_path=agg*
{
    "size": 100,
    "aggs": {
        "values": {
            "terms": {
                "field": "Extension.keyword",
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
get libgen/_search
{"query": {"query_string": {"query": "Alice in Wonderland", "fields": ["content"]}}}

POST libgen/_update/874611_d5c5af05d51c83da3a4cb833d5e830f7
{
  "doc": {
    "content": "Alice in Wonderland "
  }
}