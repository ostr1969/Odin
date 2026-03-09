#!/bin/bash
shopt -s expand_aliases
alias PUT='curl  -H "Content-Type: application/json"   -XPUT '
alias POST='curl  -H "Content-Type: application/json"   -XPOST '
alias DELETE='curl  -H "Content-Type: application/json"   -XDELETE '
alias GET='curl  -H "Content-Type: application/json"   -XGET '
DELETE "http://172.17.0.1:9200/libgen_chunks"
echo

PUT "http://172.17.0.1:9200/libgen_chunks" -d'
{
   "mappings": {
    "properties": {
      "doc_id": { "type": "keyword" },
      "chunk_id": { "type": "integer" },
      "content": { "type": "text","analyzer": "hun_ana" },
      "embedding": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      }
    }
  },
    "settings" : {
      "index" : {
      "number_of_shards": "8",
      "number_of_replicas": 0,
      "refresh_interval": "1s",
        "analysis" : {
          "filter" : {
            "wordnet_filter" : {
              "format" : "wordnet",
              "expand" : "false",
              "type" : "synonym",
              "synonyms_path" : "wn_s.pl"
            },
            "hunspell" : {
              "locale" : "en_US",
              "type" : "hunspell"
            },
            "NASA_filter" : {
              "type" : "synonym",
              "synonyms_path" : "NASA.json",
              "expand" : "false"
            }
          },
          "analyzer" : {
          "simple_split": {
        "type": "custom",
        "tokenizer": "standard",
        "filter": [
          "lowercase"
        ]
      },
            "wordnet_ana" : {
              "filter" : [
                "wordnet_filter",
                "kstem",
                "hunspell",
                "kstem",
                "stop"
              ],
              "tokenizer" : "standard"
            },
            "hun_ana" : {
              "filter" : [
                "hunspell",
                "kstem",
                "apostrophe",
                "stop"
              ],
              "char_filter" : [
                "html_strip"
              ],
              "tokenizer" : "standard"
            }
          }
        }
      }
    }
}

'
