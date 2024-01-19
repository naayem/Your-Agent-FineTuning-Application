import streamlit as st
import pandas as pd
import json

########################################################################################################################
# SIDEBAR
########################################################################################################################
with st.sidebar:
    st.title(' JAW OpenAI FineTuning 👁️')
    st.button("Reset", type="primary")

########################################################################################################################
# TABLES
########################################################################################################################


def read_ds_into_table(path):
    # Read the JSONL file and convert it to a DataFrame
    data = []
    with open(path, 'r') as file:
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
    return df


# Display in Streamlit
st.title("Chat Logs from JSONL File")

train_df = read_ds_into_table('data/openai_ready/output_train.jsonl')
val_df = read_ds_into_table('data/openai_ready/output_valid.jsonl')
test_df = read_ds_into_table('data/openai_ready/output_test.jsonl')

num_formatted_df_rows_tr = st.slider(
    "Select number of rows to display:",
    1,
    len(train_df),
    (1, 6)
    )
with st.expander("Training set"):
    st.table(train_df.set_index('Index').iloc[num_formatted_df_rows_tr[0]-1:num_formatted_df_rows_tr[1]])

num_formatted_df_rows_val = st.slider(
    "Select number of rows to display:",
    1,
    len(val_df),
    (1, 6)
    )
with st.expander("Validation set"):
    st.table(val_df.set_index('Index').iloc[num_formatted_df_rows_val[0]-1:num_formatted_df_rows_val[1]])

num_formatted_df_rows_ts = st.slider(
    "Select number of rows to display:",
    1,
    len(test_df),
    (1, 6)
    )
with st.expander("Testing set"):
    st.table(test_df.set_index('Index').iloc[num_formatted_df_rows_ts[0]-1:num_formatted_df_rows_ts[1]])

# Note: If you have other Streamlit elements to display, you can add them accordingly.
