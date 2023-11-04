from typing import Dict, List
import openai
import streamlit as st
import time
from justai.entities.conversation import Conversation
from justai.use_cases.agent_use_cases import AgentUseCases

from justai.use_cases.conversation_use_cases import ConversationUseCases
from justai.use_cases.user_use_cases import UserUseCases


users_names = ["Vincent", "Ryan", "Hadi", "Ghadi", "Adrian", "Rouba", "Angelo", "Pigeon", "Pierre", "Jeanne"]


@st.cache_data
def open_ai_ft_models_fetch():
    classic_models = ["gpt-3.5-turbo", "gpt-4"]
    ft_openai_models = [
        model["id"] for model in openai.Model.list()["data"]
        if model["owned_by"] == "epfl-42"
    ]

    return classic_models + ft_openai_models


@st.cache_data
def users_fetch(_get_all):
    return [user.user_name for user in _get_all()]


@st.cache_data
def agents_fetch(_get_all):
    return [agent.name for agent in _get_all()]


########################################################################################################################
# SIDEBAR
########################################################################################################################


def chatbot_sidebar(
    user_use_cases: UserUseCases,
    agent_use_cases: AgentUseCases,
    conversation_use_cases: ConversationUseCases
):
    '''
    This function is used to create the sidebar of the chatbot page.
    It needs to get the repositories to interact with the user, agent and conversation databases
    Ex: It gets the repos variable from the database_sidebar function for example.


    '''
    which_conversation = None

    if "user" not in st.session_state:
        st.session_state.user = "None"

    if "agent" not in st.session_state:
        st.session_state.agent = "None"

    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = None

    if "flag_save" not in st.session_state:
        st.session_state.flag_save = False

    with st.sidebar:
        st.title(' JAW OpenAI Agents 👁️')

        st.session_state["openai_model"] = open_ai_ft_models_fetch()

        st.session_state["selected_fine_tuned_model"] = st.selectbox(
            "Select a fine tuned model",
            st.session_state["openai_model"]
        )

        with st.expander('👨‍💻 User Setup'):
            st.session_state.user = st.selectbox(
                "Select a user",
                users_fetch(user_use_cases.get_all)
            )

            st.session_state.agent = st.selectbox(
                "Select a Agent",
                agents_fetch(agent_use_cases.get_all)
            )

        agent_convos = conversation_use_cases.get_by_agent_name(st.session_state.agent)
        user_convos = conversation_use_cases.search_in_conversations_by_tag(agent_convos, st.session_state.user)
        labels = conversation_use_cases.extract_labels_from_conversations(user_convos)
        labels["New conversation"] = "New conversation"
        which_conversation_name = st.radio("Select a conversation", labels)
        which_conversation_id = labels[which_conversation_name]
        current_conversation = st.session_state.current_conversation

        if st.button("Save current conversation"):
            st.session_state.flag_save = True

        if st.session_state.flag_save:
            with st.form("save_conversation"):
                conversation_name = st.text_input("Conversation name")
                submit_save_conv = st.form_submit_button("Submit save conversation")
                if submit_save_conv:
                    if which_conversation_id.id == "New conversation" and current_conversation is not None:
                        current_conversation.tags = [st.session_state.user, "label: " + conversation_name]
                        conv_review = conversation_use_cases.create(
                            current_conversation.agent_name,
                            [message.to_dict() for message in current_conversation.messages],
                            tags=current_conversation.tags
                        )
                        st.write(conv_review)
                    elif st.session_state.current_conversation is not None:
                        current_conversation.tags = [st.session_state.user, "label: " + conversation_name]
                        st.session_state.current_conversation.id = which_conversation_id.id
                        st.write(current_conversation)
                        conversation_use_cases.overwrite_not_efficient(current_conversation)
                    st.warning("Not implemented")
                    st.success(f"Conversation {conversation_name} saved!")
                    st.session_state.flag_save = False
                    time.sleep(5)
                    st.rerun()
    if which_conversation_id.id == "New conversation":
        st.session_state.current_conversation = Conversation(
            agent_name=st.session_state.agent,
            messages=[],
            tags=[st.session_state.user]
        )
    else:
        which_conversation = which_conversation_id
        st.session_state.current_conversation = which_conversation

    return which_conversation
