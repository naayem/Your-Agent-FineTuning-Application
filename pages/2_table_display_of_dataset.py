import streamlit as st
import pandas as pd
import json

# Read the JSONL file and convert it to a DataFrame
data = []
with open('data/openai_ready/output_test.jsonl', 'r') as file:
    for line in file:
        data.append(json.loads(line))

# Extract messages and format them
roles = []
contents = []
indices = []
for idx, entry in enumerate(data, 1):
    for message in entry["messages"]:
        roles.append(message["role"].upper())
        contents.append(message["content"])
        # Only add the index for the first role in each group (for the SYSTEM role)
        if message["role"] == "system":
            indices.append(idx)
        else:
            indices.append('')

df = pd.DataFrame({
    'Index': indices,
    'Role': roles,
    'Content': contents
})

# Display in Streamlit
st.title("Chat Logs from JSONL File")
st.table(df.set_index('Index'))

# Note: If you have other Streamlit elements to display, you can add them accordingly.
