import getpass
import locale; locale.getpreferredencoding = lambda: "UTF-8"
import os
import torch
import streamlit as st


import numpy as np
import altair as alt
import pandas as pd
import datetime as dt
import time

from justai.old.fineTuningfunctions import import_gen_dataset
from justai.old.cells_content import cell_prompt_templating_and_zero_shot_inference
from justai.old.cells_content import display_code_generation_dataset
from justai.old.cells_content import display_prompt_templating_zero_shot_code
from justai.old.fineTuningfunctions import zero_shot_run


# App title
st.set_page_config(page_title="JAW Llama2 FineTuning 🦙", layout="wide")

with st.sidebar:
    st.title(' JAW Llama2 Chatbot 🦙')
    if 'HF_API_TOKEN' in st.secrets:
        st.success('Hugging Face API key provided!', icon='✅')
    else:
        hugging_face_api = st.text_input(
            "Enter a Hugging Face API token ",
            value="",
            type="password")
        if not (hugging_face_api.startswith('hf_')
                and len(hugging_face_api) == 37):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to explore Fine Tuning!', icon='👉')

    st.button("Reset", type="primary")

st.header('Fine Tuning Experimentation')

st.subheader('Import The Code Generation Dataset 📋')

display_code_generation_dataset()

code_generation_dataframe = import_gen_dataset()

num_df_rows = st.slider("Select number of rows to display:",
                        1,
                        len(code_generation_dataframe))
st.write(code_generation_dataframe.head(num_df_rows))


st.subheader("Prompt Templating and Zero Shot Inference")
cell_prompt_templating_and_zero_shot_inference()
display_prompt_templating_zero_shot_code()
# zero_shot_run(code_generation_dataframe)










# Example 3
df_test_streamlit = pd.DataFrame({
     'première colonne': [1, 2, 3, 4],
     'deuxième colonne': [10, 20, 30, 40]
     })

# Example 5
np.random.seed(42)  # You can choose any number for the seed

df2 = pd.DataFrame(
     np.random.randn(200, 3),
     columns=['a', 'b', 'c'])
c = alt.Chart(df2).mark_circle().encode(
     x='a', y='b', size='c', color='c', tooltip=['a', 'b', 'c'])
st.write("\n voila un graphe de altair", c, "C'est joli")

st.markdown('📖 Learn how to build this app in this [blog]\
(https://towardsdatascience.com/how-to-build-a-llama2-chatbot-with-streamlit-\
and-replicate-ai-2f8a8f2b9d3b) post.')

st.latex(r'''
     a + ar + a r^2 + a r^3 + \cdots + a r^{n-1} =
     \sum_{k=0}^{n-1} ar^k =
     a \left(\frac{1-r^{n}}{1-r}\right)
    ''')
st.caption('A caption with _italics_ :blue[colors] and emojis :sunglasses:')
