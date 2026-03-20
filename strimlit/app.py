import streamlit as st
import requests
#print(st.session_state)
globs=["pharse","ind"]
for g in globs:
    if g  in st.session_state:
        st.session_state[g] = st.session_state[g]
     


create_page = st.Page("pages/create.py", title="Create entry", icon=":material/add_circle:")
delete_page = st.Page("pages/delete.py", title="Delete entry", icon=":material/delete:")
chat_page = st.Page("pages/chat.py", title="Chat", icon=":material/chat:")
home_page = st.Page("pages/home.py", title="Home", icon=":material/house:")
search_page = st.Page("pages/search.py", title="Search", icon=":material/search:")
#st.session_state["_b"]=""
pg = st.navigation([home_page, search_page, chat_page, create_page, delete_page])

pg.run()