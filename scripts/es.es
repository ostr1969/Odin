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