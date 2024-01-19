import uuid
import streamlit as st
import openai

import justai
from justai.interface_adapters.mappers import map_to_conversation
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases
from justai.use_cases.user_use_cases import UserUseCases

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

if "conversation_tree" not in st.session_state.keys():
    st.session_state.conversation_tree = [{"role": "assistant", "content": "How may I assist you today?"}]


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


def rerun_chat_from_index(idx):
    st.session_state.messages = st.session_state.messages[:idx+1]


########################################################################################################################
# SIDEBAR
########################################################################################################################
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()
openai_api_key = justai.frameworks_and_drivers.llm_sidebar.llm_sidebar()
user_use_cases = UserUseCases(repos["user"])
agent_use_cases = AgentUseCases(repos["agent"], repos["backup"], repos["conversation"])
conversation_use_cases = ConversationUseCases(repos["agent"], repos["conversation"], repos["backup"])

which_conversation = justai.frameworks_and_drivers.chatbot_sidebar.chatbot_sidebar(user_use_cases, agent_use_cases, conversation_use_cases)

if st.session_state.current_conversation is not None:
    messages = st.session_state.current_conversation.messages
    st.session_state.messages = [message.to_dict() for message in messages if message.role != "system"]
########################################################################################################################
# Chatbot
########################################################################################################################

st.title(f"💬 Chat with {st.session_state.agent}")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

with st.expander("Edit a message"):
    msg_idx_to_edit = st.number_input(
        "index of message to edit",
        min_value=0,
        max_value=len(st.session_state.messages),
        value=0
    )
    st.write(st.session_state.messages)
    msg_to_edit = st.session_state.messages[msg_idx_to_edit]["content"]
    msg_to_edit = st.text_area("edit message", value=msg_to_edit)
    st.session_state.messages[msg_idx_to_edit]["content"] = msg_to_edit
    c1, c2 = st.columns(2)
    c1.button("Rerun from message index", on_click=rerun_chat_from_index, args=(msg_idx_to_edit,))
    c2.number_input("Conversation Tree", min_value=0, max_value=len(st.session_state.conversation_tree) - 1, value=0)

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"], st.number_input(uuid.uuid1().__str__(), step=1, label_visibility="hidden"))


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

st.session_state.current_conversation = map_to_conversation(st.session_state.messages, st.session_state.agent)
