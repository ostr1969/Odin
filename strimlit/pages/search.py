import streamlit as st
import config
from config import es
from utils import build_query,get_topics_dn
from dialogs.searchdialogs import yeardialog,typedialog,topicsdialog
from streamlit_extras.mention import mention
import streamlit.components.v1 as components
res=None
if "navigation_source" in st.session_state:
        del st.session_state.navigation_source

print(st.session_state)          
def firstsearch(filters):
    
    q=build_query(filters)
    res = es.search(
            index=st.session_state.ind,
            track_total_hits=True,
            query=q,
            size=100,
            
            aggregations={
               
                    "topics": {
                        "terms": {
                            "field": "topics.id",
                            "size": 10
                            }
                    
                }, 
                    "types":{ "terms": { "field": "type", "size": 10 } }
            }
        )
    print(res["hits"]["total"]["value"])
    return res
field_options=["title","abstract+title","abstract+title+content"]

with st.container(border=True):
    with st.container(border=False,horizontal=True,vertical_alignment="bottom",horizontal_alignment="distribute"):
        st.text_input("search phrase", key="pharse",placeholder="Enter search phrase", on_change=firstsearch,label_visibility="hidden")
        st.button("Apply")
    with st.container(border=False,horizontal=True,vertical_alignment="bottom",horizontal_alignment="distribute"):
        st.selectbox("search in", config.INDEXES, key="ind",width=150,)
        st.selectbox("search fields", field_options, key="searchfields",width=250,)
if st.session_state.get("pharse"):
    filters=[{"field":st.session_state.searchfields,"value":st.session_state.pharse}]
    if st.session_state.get("dchoice") == "0":
        filters.append({"field":"publication_year","from":2025,"to":3000})
    elif st.session_state.get("dchoice") == "1":
        filters.append({"field":"publication_year","from":2020,"to":3000})
    elif st.session_state.get("dchoice") == "custom":       
        filters.append({"field":"publication_year","from":st.session_state.get("from_year"),"to":st.session_state.get("to_year")})
    if st.session_state.get("type_filters"):
        filters.append({"field":"types","value":st.session_state.get("type_filters")})  
    if st.session_state.get("oa_filter"):
        filters.append({"field":"primary_location.is_oa","value":True})  
    res=firstsearch(filters)  
         
if  res is not None:
    topics = res["aggregations"]["topics"]["buckets"]
    topicsdn=get_topics_dn(topics,index=st.session_state.ind)
    types = res["aggregations"]["types"]["buckets"]
    total = res["hits"]["total"]["value"]
    results = [hit["_source"] for hit in res["hits"]["hits"]]
    with st.container(horizontal=True,vertical_alignment="bottom",horizontal_alignment="left"):
        st.button("Year ▾", on_click=yeardialog)
        st.button("Document types ▾", on_click=lambda: typedialog(types))
        st.toggle("Open access",key="oa_filter")
        st.button("Topics ▾", on_click=lambda: topicsdialog(topicsdn))
    with st.container(border=True):
        st.subheader(f"Found {total:,} results")
        st.markdown("---") 
        for r in results:
            if r.get("type")=="book" or r.get("type")=="book-chapter":
                icon="📚"
            elif r.get("type")=="article":
                icon="📄"
            elif r.get("type")=="chapter":
                icon="📖"
            elif r.get("type")=="dataset":
                icon="📦"
            elif r.get("type")=="dissertation":
                icon="🎓"
            else:                icon="📁"
            m=mention(label=r.get("type"),icon=icon, url=r.get("id"), write=False)
            st.markdown(f"{m},\"{r['title']}\"",unsafe_allow_html=True)   
