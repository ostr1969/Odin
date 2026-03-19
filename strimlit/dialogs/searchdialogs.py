import streamlit as st



@st.dialog("Year Filter",width="medium")
def yeardialog():
        #col1, col2, col3 = st.columns(3)
        print("A:",st.session_state)
        
        #st.markdown('<div class="narrowbutton">',unsafe_allow_html=True)
        if st.button("Since 2025",type="tertiary"):            
            
            st.session_state["dchoice"] = "0"
           
            st.rerun()
              
        if st.button("Since 2020",type="tertiary"):
            st.session_state["dchoice"] = "1"
            
            st.rerun()
        with st.container(horizontal=True,vertical_alignment="bottom",horizontal_alignment="left"):
            if st.button("Custom range...",type="tertiary"):
                st.session_state["dchoice"] = "custom"
            if st.session_state.get("dchoice","") == "custom":
                fromyear=st.session_state.get("fromyear",2000)
                toyear=st.session_state.get("toyear",2100)
                st.number_input("from", key="from_year",placeholder="From year",
                                    label_visibility="hidden",min_value=0,max_value=2100,step=10,value=fromyear,width=150)
                st.number_input("to", key="to_year",placeholder="To year",
                                    label_visibility="hidden",min_value=0,max_value=2100,step=10,value=toyear,width=150)
                if st.button("Apply",type="primary"):
                    st.session_state["fromyear"] = st.session_state["from_year"]
                    st.session_state["toyear"] = st.session_state["to_year"]                  
                    st.rerun()
                #st.rerun()
        #st.markdown('</div>',unsafe_allow_html=True)            
          
@st.dialog("Document types",width="small")
def typedialog(types):
    for t in types:
        st.checkbox(f"{t['key']} ({t['doc_count']})", key=f"type_{t['key']}")
    if st.button("Apply",type="primary"):
        st.session_state["type_filters"] = [t for t in types if st.session_state.get(f"type_{t['key']}")]
        st.rerun()
@st.dialog("Topics",width="small")
def topicsdialog(topics):
    #print("topic:",topics)
    for t,v in topics.items():
        
        st.checkbox(f"{v[0]} ({v[1]})", key=f"topic_{t}")
    if st.button("Apply",type="primary"):
        st.session_state["topic_filters"] = [t for t in topics if st.session_state.get(f"topic_{t}")]
        st.rerun()        