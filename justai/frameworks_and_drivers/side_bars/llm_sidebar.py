import streamlit as st
import openai

########################################################################################################################
# SIDEBAR
########################################################################################################################


def llm_sidebar():
    with st.sidebar:
        with st.expander('🔑 OpenAI API Key'):
            if 'OPENAI_TOKEN' in st.secrets:
                openai_api_key = st.secrets['OPENAI_TOKEN']
<<<<<<< HEAD
                openai.api_key = openai_api_key
=======
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
                st.success('OpenAI API key provided!', icon='✅')
            else:
                openai_api_key = st.text_input(
                    "Enter an OpenAI API token ",
                    value="",
                    type="password").strip('"')
                if not (openai_api_key.startswith('sk-')
                        and len(openai_api_key) == 51):
                    openai_api_key = None
                    st.warning('Please enter your credentials!', icon='⚠️')
                else:
                    st.success('Proceed to explore Fine-Tuning!', icon='👉')

            st.button("Reset", type="primary")
<<<<<<< HEAD
    return openai_api_key
=======
    return openai.OpenAI(api_key=openai_api_key)
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
