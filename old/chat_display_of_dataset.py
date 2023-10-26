import streamlit as st
import json


# Read the JSONL file and display in Streamlit
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Open the json line file and count the number of lines
with open('data/openai_ready/output_test.jsonl', 'r') as file:
    programming_ds_len = len(file.readlines())

st.write(programming_ds_len)
chat_idx_start, chat_idx_end = st.slider(label="Select number of chat to display:",
                                         min_value=1,
                                         max_value=programming_ds_len,
                                         value=(5, 10))
with open('data/openai_ready/output_test.jsonl', 'r') as file:
    for i, line in enumerate(file):
        if i == chat_idx_end:
            break
        if i >= chat_idx_start:
            chat_entry = json.loads(line)
        else:
            continue
        for message in chat_entry['messages']:
            if message["role"] != "system":
                # Display assistant message in chat message container
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
