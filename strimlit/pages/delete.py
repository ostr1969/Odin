import streamlit as st
from  app import store_value, load_value
print(st.session_state)

st.badge("Delete entry")
#load_value("_b","b1")

st.text_input("Entry name", key="b")
