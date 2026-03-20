import streamlit as st



@st.dialog("Year Filter",width="medium")
def yeardialog():
        with st.container(gap=None):
            if st.button("Since 2025",type="tertiary"):            
                
                st.session_state["filters"]["dchoice"] = "0"
            
                st.rerun()
                
            if st.button("Since 2020",type="tertiary"):
                st.session_state["filters"]["dchoice"] = "1"
                
                st.rerun()
            with st.container(horizontal=True,vertical_alignment="bottom",horizontal_alignment="left"):
                if st.button("Custom range...",type="tertiary"):
                    st.session_state["filters"]["dchoice"] = "custom"
                if st.session_state["filters"].get("dchoice","") == "custom":
                    fromyear=st.session_state["filters"].get("from_year",2000)
                    toyear=st.session_state["filters"].get("to_year",2100)
                    st.number_input("from", key="from_year",placeholder="From year",
                                        label_visibility="hidden",min_value=0,max_value=2100,step=10,value=fromyear,width=150)
                    st.number_input("to", key="to_year",placeholder="To year",
                                        label_visibility="hidden",min_value=0,max_value=2100,step=10,value=toyear,width=150)
                    if st.button("Apply",type="primary"):
                        st.session_state["filters"]["from_year"] = st.session_state["from_year"]
                        st.session_state["filters"]["to_year"] = st.session_state["to_year"]                  
                        st.rerun()
            if st.button("Clear",type="primary"):
                if "dchoice" in st.session_state["filters"]:
                    del st.session_state["filters"]["dchoice"]            
                st.rerun()
        #st.markdown('</div>',unsafe_allow_html=True)            
          
@st.dialog("Document types",width="small")
def typedialog(types):
    for t in types:
        st.checkbox(f"{t['key']} ({t['doc_count']})", key=f"type_{t['key']}")
    if st.button("Apply",type="primary"):
        st.session_state["filters"]["type_filters"] = [t["key"] for t in types if st.session_state.get(f"type_{t['key']}")]
        st.rerun()
@st.dialog("Language",width="small")        
def langdialog(languages):
    for t in languages:
        st.checkbox(f"{t['key']} ({t['doc_count']})", key=f"language_{t['key']}")
    if st.button("Apply",type="primary"):
        st.session_state["filters"]["language_filters"] = [t["key"] for t in languages if st.session_state.get(f"language_{t['key']}")]
        st.rerun()        
@st.dialog("Topics",width="small")
def topicsdialog(topics):
    httpcut={}
    for t,v in topics.items():
        t1=t.replace("https://openalex.org/","")
        httpcut[t1]=t #long to short
        #st.checkbox(f"{v[0]} ({v[1]})", key=f"topic_{t1}")
        st.checkbox(f"{v[0]} ({t1})", key=f"topic_{t1}")
    if st.button("Apply",type="primary"):
        st.session_state["filters"]["topic_filters"] = [v for t,v in httpcut.items() if st.session_state.get(f"topic_{t}")]
        st.rerun() 
@st.dialog("Concepts",width="small")
def conceptsdialog(concepts):
    httpcut={}
    for t,v in concepts.items():
        t1=t.replace("https://openalex.org/","")
        httpcut[t1]=t #long to short
        #st.checkbox(f"{v[0]} ({v[1]})", key=f"concept_{t1}")
        st.checkbox(f"{v[0]} ({t1})", key=f"concept_{t1}")
    if st.button("Apply",type="primary"):
        st.session_state["filters"]["concept_filters"] = [v for t,v in httpcut.items() if st.session_state.get(f"concept_{t}")]
        st.rerun()                