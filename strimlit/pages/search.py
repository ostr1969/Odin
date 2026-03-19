import streamlit as st
import config
from config import es
from utils import build_query

if "navigation_source" in st.session_state:
        del st.session_state.navigation_source

print(st.session_state)          
def firstsearch():
    filters=[{"field":"abstract+title","value":st.session_state.pharse}]
    body=build_query(filters)
    res = es.search(
            index=st.session_state.ind,
            track_total_hits=True,
            body={
                **body,
                "aggs": {
                    "topics": {
                        "terms": {
                            "field": "topics.id",
                            "size": 10
                            }
                    }
                }
            }
        )
    print(res["hits"]["total"]["value"])
    return res
field_options=["title","abstract+title","abstract+title+content"]

with st.container(border=True):
    with st.container(border=False,horizontal=True,vertical_alignment="bottom",horizontal_alignment="distribute"):
        st.text_input("search phrase", key="pharse",placeholder="Enter search phrase", on_change=firstsearch,label_visibility="hidden")
        st.button("Apply", on_click=firstsearch)
    with st.container(border=False,horizontal=True,vertical_alignment="bottom",horizontal_alignment="distribute"):
        st.selectbox("search in", config.INDEXES, key="ind",width=150,)
        st.selectbox("search fields", field_options, key="searchfields",width=250,)
if st.session_state.get("pharse"):
    res=firstsearch()        
if  res:
    topics = res["aggregations"]["topics"]["buckets"]
    total = res["hits"]["total"]["value"]
    results = [hit["_source"] for hit in res["hits"]["hits"]]
    with st.container(border=True):
        st.subheader(f"Found {total} results")
        st.markdown("---") 
        for r in results:
            st.markdown(f"**{r['title']}**")   