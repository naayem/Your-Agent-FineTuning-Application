import streamlit as st
import openai

########################################################################################################################
# SIDEBAR
########################################################################################################################
with st.sidebar:
    st.title(' JAW OpenAI FineTuning 👁️')
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

    st.session_state["openai_model"] = [model["id"] for model in openai.Model.list()["data"] if model["owned_by"] == "epfl-42"]

    selected_fine_tuned_model = st.selectbox("Select a fine tuned model", st.session_state["openai_model"])

########################################################################################################################
# Chatbot
########################################################################################################################

st.title("💬 Chatbot with with your fine tuned model")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


if prompt := st.chat_input("What is up?"):
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    messages = [
                {"role": "system", "content": "JustAProgrammer is a programming assistant."},
                *({"role": m["role"], "content": m["content"]} for m in st.session_state.messages)
            ]

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"][0],
            messages=[
                {"role": "system", "content": "JustAProgrammer is a programming assistant."},
                *({"role": m["role"], "content": m["content"]} for m in st.session_state.messages)
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
