import streamlit as st
from  app import store_value, load_value
print(st.session_state)

st.text_input("Create entry", key="b")


