import streamlit as st
import config
from config import es

print(st.session_state)
# Check if rerun is due to navigation or direct access
if 'navigation_source' not in st.session_state:
    st.session_state.navigation_source = 'direct_access'  # Default for direct access
    if "pharse" in st.session_state:
        del st.session_state.pharse
st.title("OA&LG Search",text_alignment="center")
if st.session_state.get("ind"): 
    cnt=es.count(index=st.session_state.ind)
else:
    cnt = es.count(index="works3")
cnt=cnt["count"]//1000000    
st.subheader(f"Search over {cnt}M articles and books of OA&LG content")
field_options=["title","abstract+title","abstract+title+content"]
if not st.session_state.get("searchfields"):
     st.session_state["searchfields"]="title"  


with st.container(border=True):
    st.text_input("search phrase", key="pharse",placeholder="Enter search phrase",label_visibility="hidden")
    with st.container(border=False,horizontal=True,vertical_alignment="bottom",horizontal_alignment="distribute"):
        st.selectbox("search index", config.INDEXES, key="ind",width=150,)
        st.selectbox("search fields", field_options, key="searchfields",width=250,)
if st.session_state.get("pharse"):
    st.switch_page("pages/search.py")        