from typing import List, Dict
import pandas as pd
from justai.entities.conversation import Conversation
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases
import streamlit as st

from streamlit_extras.dataframe_explorer import dataframe_explorer

if "user" not in st.session_state:
    st.session_state.user = "None"
if "agent" not in st.session_state:
    st.session_state.agent = "None"


def generate_dummy_conversation(selected_agent_cf_prompt: str, nb_exchanges: int) -> List[Dict]:
    messages = [{"role": "system", "content": selected_agent_cf_prompt}]

    for i in range(nb_exchanges):
        user_message = f"user_message{i}"
        assistant_message = f"assistant_message{i}"
        messages.append(
            {
                "role": "user",
                "content": user_message
                }
            )
        messages.append(
            {
                "role": "assistant",
                "content": assistant_message
                }
            )

    return messages


def conversation_column_headers():
    """
    Return column headers for a conversation dataframe.
    """
    return '''
    - **ID**: Unique identifier assigned to each conversation.
    - **Agent Name**: Each conversation is linked to an unique agent.
    - **Tags**: Tags are used to store information such as username of creator, label of a conversations etc..
    - **Messages**: Messages are the actual conversation between the user and the agent.
    Each message contains a role and content. Each conversation contains one system message,
    and an arbitrary number of user and assistant messages.'''


def flatten_conversation(convo):
    """
    Flatten a conversation dictionary into a flattened dictionary.
    """
    # Extracting id, agent_name, and tags
    flattened = {
        "id": convo["id"],
        "agent_name": convo["agent_name"],
        "tags": ', '.join(convo["tags"])
    }
    # Convert the messages list into a single string
    messages_str = ' | '.join([f"{msg.split(',')[0].split('=')[1]}:\
        {msg.split(',')[1].split('=')[1][:-1]}" for msg in convo["messages"]])
    flattened["messages"] = messages_str
    return flattened


def display_conversations(conversations: List[Conversation]):
    all_conversations_for_df = [conversation.to_dict_stringify_messages() for conversation in conversations]
    flattened_conversations = [flatten_conversation(convo) for convo in all_conversations_for_df]
    flattened_df = pd.DataFrame(flattened_conversations)
    filtered_conv_df = dataframe_explorer(flattened_df, case=False)
    st.dataframe(filtered_conv_df, use_container_width=True)


def create_conversation(
    agent_use_cases: AgentUseCases,
    conversation_use_cases: ConversationUseCases,
    agent_names: List[str]
):
    """
    Create a new conversation in the system.
    """
    nb_exchanges = st.number_input(
        "Number of Messages desired in the conversation",
        value=1,
        min_value=1,
        max_value=1000,
        step=1
    )
    try:
        default_index = agent_names.index(st.session_state.agent)
    except ValueError:
        default_index = 0
    selected_agent_name = st.selectbox(
        "Select Agent linked to the conversation",
        agent_names,
        index=default_index
        )
    st.session_state.agent = selected_agent_name
    selected_agent = None
    if selected_agent_name:
        selected_agent = agent_use_cases.get_one(selected_agent_name)
        dummy_messages = generate_dummy_conversation(selected_agent.system_prompt, nb_exchanges)
    else:
        st.warning("No agent selected")
        dummy_messages = []

    with st.form("Create Conversation form"):
        if selected_agent:
            st.write(f"Selected Agent: {selected_agent.name}")
            st.text(f"System Prompt: {selected_agent.system_prompt}")

        messages = st.data_editor(dummy_messages, use_container_width=True)
        submit_conversation = st.form_submit_button("Create Conversation")

        if submit_conversation and messages and selected_agent:
            try:
                conversation_use_cases.create(selected_agent.name, messages)
                st.success("Conversation created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def remove_conversation(conversation_use_cases: ConversationUseCases):
    """
    Delete a conversation from the system.
    """
    with st.form("Remove Conversation form"):
        conversation_id = st.text_input("Insert Conversation ID").strip('"').strip("'")
        delete_conversation = st.form_submit_button("Remove Conversation")

        if delete_conversation and conversation_id:
            try:
                conversation_use_cases.delete_by_id(conversation_id)
                st.success(f"Conversation {conversation_id} removed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def conversation_management_dashboard(
    agent_use_cases: AgentUseCases,
    conversation_use_cases: ConversationUseCases,
    agent_names: List[str],
    conversations: List[Conversation],
    expander: False
):
    # Display the conversations
    st.header("Conversation Management Dashboard")
    st.subheader("Conversation Directory")
    st.caption("Conversations provide real-world context, making models adaptable and responsive.\
        They simulate human interaction, crucial for an agent's effectiveness.")
    conversation_column_headers = '''
    - **ID**: Unique identifier assigned to each conversation.
    - **Agent Name**: Each conversation is linked to an unique agent.
    - **Tags**: Tags are used to store information such as username of creator, label of a conversations etc..
    - **Messages**: Messages are the actual conversation between the user and the agent.
    Each message contains a role and content. Each conversation contains one system message,
    and an arbitrary number of user and assistant messages.'''
    if expander:
        exp_conv = st.expander("Column Headers:")
        exp_conv.markdown(conversation_column_headers)
    else:
        st.markdown("**Column Headers:**")
        st.markdown(conversation_column_headers)
    display_conversations(conversations)

    # Add a new conversation
    st.subheader("Create a new conversation")
    st.caption("Create a new conversation by selecting an agent and providing a list of messages.\
        Select a number of messages to fit the length of the desired conversation.\
        Only the content of the messages is required to be modified. The role needs to remain untouched.\
        In a further version, the role will be automatically assigned or freezed to the user or the assistant")
    create_conversation(agent_use_cases, conversation_use_cases, agent_names)

    # Delete a conversation
    st.subheader("Remove a conversation")
    st.caption("Find the conversation's id in the directory above and enter it below to remove it from the system.\
        A copy paste will suffice.")
    remove_conversation(conversation_use_cases)
