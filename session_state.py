# session_state.py

import streamlit as st

def init_session_state():
    defaults = {
        "consent": False,
        "input_method": "paste",
        "review_user_summary": "",
        "review_model_comparison": "",
        "review_model_judgement": "0"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
