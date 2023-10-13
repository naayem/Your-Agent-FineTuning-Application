import streamlit as st
import openai
import pandas as pd
from io import StringIO

import os
import locale

locale.getpreferredencoding = lambda: "UTF-8"

# App title
st.set_page_config(page_title="JAW OpenAI FineTuning 👁️", layout="wide")

########################################################################################################################
# SIDEBAR
########################################################################################################################
with st.sidebar:
    st.title(' JAW Llama2 Chatbot 👁️')
    if 'OPENAI_TOKEN' in st.secrets:
        openai_api_key = st.secrets['OPENAI_TOKEN']
        openai.api_key = openai_api_key
        st.success('OpenAI API key provided!', icon='✅')
    else:
        openai_api_key = st.text_input(
            "Enter an OpenAI API token ",
            value="",
            type="password")
        if not (openai_api_key.startswith('sk-')
                and len(openai_api_key) == 51):
            openai_api_key = None
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to explore Fine Tuning!', icon='👉')

    st.button("Reset", type="primary")

########################################################################################################################
# Home Page
########################################################################################################################

st.title('JAW OpenAI Spinning Off Agents 👁️')
st.header('This is my home page I have to be creative here')
st.write("Let'show a dashboard of the current openAI jobs and let's maybe have a readme home page")
