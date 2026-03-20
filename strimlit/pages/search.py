import streamlit as st
import config

from utils import build_query,get_topics_dn,mybutton,get_concepts_dn,firstsearch,download
from dialogs.searchdialogs import yeardialog,typedialog,topicsdialog,langdialog,conceptsdialog,file_dialog
from streamlit_extras.mention import mention
import streamlit.components.v1 as components
res=None
st.set_page_config(layout="wide")
if "navigation_source" in st.session_state:
        del st.session_state.navigation_source
if "filters" not in st.session_state:        
    st.session_state.filters = {}

#print(st.session_state)          

field_options=["title","abstract+title","abstract+title+content"]

with st.container(border=True,width="stretch"):
    with st.container(border=False,horizontal=True,vertical_alignment="bottom",horizontal_alignment="distribute"):
        st.text_input("search phrase", key="pharse",placeholder="Enter search phrase",label_visibility="hidden")
        st.button("Apply")
    with st.container(border=False,horizontal=True,vertical_alignment="bottom",horizontal_alignment="distribute"):
        st.selectbox("search in", config.INDEXES, key="ind",width=150,)
        st.selectbox("search fields", field_options, key="searchfields",width=250,)
if st.session_state.get("pharse"):
    filters=[{"field":st.session_state.searchfields,"value":st.session_state.pharse}]
    if st.session_state["filters"].get("dchoice") == "0":
        filters.append({"field":"publication_year","from":2025,"to":3000})
    elif st.session_state["filters"].get("dchoice") == "1":
        filters.append({"field":"publication_year","from":2020,"to":3000})
    elif st.session_state["filters"].get("dchoice") == "custom":       
        filters.append({"field":"publication_year","from":st.session_state["filters"].get("from_year"),"to":st.session_state["filters"].get("to_year")})
    if st.session_state["filters"].get("type_filters"):
        filters.append({"field":"type","value":st.session_state["filters"].get("type_filters")}) 
    if st.session_state["filters"].get("topic_filters"):
        filters.append({"field":"topics.id","value":st.session_state["filters"].get("topic_filters")}) 
    if st.session_state["filters"].get("concept_filters"):
        filters.append({"field":"concepts.id","value":st.session_state["filters"].get("concept_filters")})             
    if st.session_state["filters"].get("language_filters"):
        filters.append({"field":"language","value":st.session_state["filters"].get("language_filters")}) 
    if st.session_state.get("oa_filter"):
        filters.append({"field":"primary_location.is_oa","value":True})  
    res=firstsearch(filters)  
         
if  res is not None:
    topics = res["aggregations"]["topics"]["buckets"]
    topicsdn=get_topics_dn(topics,index=st.session_state.ind)
    concepts = res["aggregations"]["concepts"]["buckets"]
    conceptsdn=get_concepts_dn(concepts,index=st.session_state.ind)
    types = res["aggregations"]["types"]["buckets"]
    languages = res["aggregations"]["language"]["buckets"]
    total = res["hits"]["total"]["value"]
    results = [hit["_source"] for hit in res["hits"]["hits"]]
    with st.container(horizontal=True,vertical_alignment="center",horizontal_alignment="left",gap="xxsmall"):
        mybutton("Year ▾", on_click=yeardialog,key="year_button",
                 reversed=st.session_state["filters"].get("dchoice","")!="")
        mybutton("Document types ▾", on_click=lambda: typedialog(types),key="type_button",
                 reversed=(st.session_state["filters"].get("type_filters",[])!=[]))
        
        mybutton("Topics ▾", on_click=lambda: topicsdialog(topicsdn),key="topic_button",
                 reversed=(st.session_state["filters"].get("topic_filters",[])!=[]))
        mybutton("Concepts ▾", on_click=lambda: conceptsdialog(conceptsdn),key="concept_button",
                 reversed=(st.session_state["filters"].get("concept_filters",[])!=[]))
        
        mybutton("Language ▾", on_click=lambda: langdialog(languages),key="language_button",
                 reversed=(st.session_state["filters"].get("language_filters",[])!=[]))
        st.toggle("Open access",key="oa_filter")
        st.button("Clear filters", on_click=lambda: st.session_state.update({"filters": {}}),key="clear_button",type="primary")
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
            
            url = f"/json?index={st.session_state.ind}&id={r.get('id').replace('https://openalex.org/','')}"
            #st.markdown(f"{icon},\"{r['title']}\",{r.get('publication_year')}",unsafe_allow_html=True)   
            with st.container(horizontal=True,vertical_alignment="center",horizontal_alignment="left",gap="xxsmall"):
                st.markdown(
                f'{icon} <a href="{url}" style="text-decoration:none; " target="_blank">'
                f'"{r["title"]}"</a>, {r.get("publication_year")}'
                , unsafe_allow_html=True
                )
                
                st.button("📥",type="tertiary", on_click=lambda id=r.get("id"): download(id),
                          key=f"file_button_{r.get('id')}")
                
                