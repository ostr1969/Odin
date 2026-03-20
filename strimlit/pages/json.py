import streamlit as st
st.set_page_config(layout="wide")
id_value = st.query_params.get("id")
ind=st.query_params.get("index","works3")
#lnk="https://openalex.org/"+id_value
from config import es
j=es.get(index=ind, id=id_value)["_source"]
st.json(j)