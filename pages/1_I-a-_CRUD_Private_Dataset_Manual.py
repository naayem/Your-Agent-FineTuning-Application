from typing import List
import streamlit as st

import justai
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases

st.set_page_config(layout="wide")


def generate_dummy_conversation(selected_agent_cf_prompt: str) -> List[dict]:
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


########################################################################################################################
# SIDEBAR
########################################################################################################################
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()

if not repos:
    st.warning("Please configure the database connection first.")

agent_use_cases = AgentUseCases(repos["agent"], repos["backup"], repos["conversation"])
conversation_use_cases = ConversationUseCases(repos["agent"], repos["conversation"], repos["backup"])

########################################################################################################################
# CRUD
########################################################################################################################
st.caption("🤖 For a better experience go to the settings and activate the wide mode")

####
# AGENTS
####
st.header("Agents")

st.subheader("Display agents")
# Display Agents
agents = agent_use_cases.get_all()
agent_names = [agent.name for agent in agents]
# Convert list of Agent objects to list of dictionaries
agents_data = [agent.to_dict() for agent in agents]
st.dataframe(agents_data)

# Add a new agent
st.subheader("Add a new agent")

with st.form("Create Agent form"):
    agent_name = st.text_input("Agent Name")
    system_prompt = st.text_input("System Prompt for Agent")
    submit_agent = st.form_submit_button("Add Agent")

    if submit_agent and agent_name and system_prompt:
        try:
            agent_use_cases.create(agent_name, system_prompt)
            st.success(f"Agent {agent_name} added successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# Delete an agent
st.subheader("Delete an agent")

with st.form("Delete Agent form"):
    selected_agent_name_to_delete = st.selectbox("Select Agent to Delete", agent_names)
    delete_agent = st.form_submit_button("Delete Agent")

    if delete_agent and selected_agent_name_to_delete:
        try:
            agent_use_cases.delete(selected_agent_name_to_delete)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# Modify an agent
st.subheader("Modify an agent")

selected_agent_name_maf = st.selectbox("Select Agent to Modify", agent_names)
current_system_prompt_maf = None
if selected_agent_name_maf:
    current_system_prompt_maf = agent_use_cases.get_one(selected_agent_name_maf).system_prompt
else:
    st.warning("No agent to modify")

with st.form("Modify Agent form"):
    st.write(selected_agent_name_maf or "tyutyduitdyi")
    new_agent_name_maf = st.text_input(
        "New Agent Name",
        value=selected_agent_name_maf or ""
    )
    new_system_prompt_maf = st.text_input(
        "New System Prompt for Agent",
        value=current_system_prompt_maf or ""
    )
    modify_agent = st.form_submit_button("Modify Agent")
    if modify_agent and not (new_system_prompt_maf):
        st.warning("Please fill in the new system prompt")
    if modify_agent and selected_agent_name_maf and new_agent_name_maf and new_system_prompt_maf:
        try:
            agent_use_cases.edit(selected_agent_name_maf, new_agent_name_maf, new_system_prompt_maf)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
####
# CONVERSATIONS
####

# Display the conversations
st.header("Conversations")
all_conversations = conversation_use_cases.get_all()
st.write(all_conversations[0])
all_conversations_for_df = [conversation.to_dict_stringify_messages() for conversation in all_conversations]
st.dataframe(all_conversations_for_df)

# Add a new conversation
st.subheader("Add a new conversation")
nb_exchanges = st.number_input("Number of Messages", value=1, min_value=1, max_value=1000, step=1)
selected_agent_name_cf = st.selectbox("Select Agent", agent_names)
selected_agent_cf = None
if selected_agent_name_cf:
    selected_agent_cf = agent_use_cases.get_one(selected_agent_name_cf)
    dummy_messages = generate_dummy_conversation(selected_agent_cf.system_prompt)
else:
    st.warning("No agent selected")
    dummy_messages = []

with st.form("Conversation form"):
    if selected_agent_cf:
        st.write(f"Selected Agent: {selected_agent_cf.name}")
        st.text(f"System Prompt: {selected_agent_cf.system_prompt}")

    messages = st.data_editor(dummy_messages, use_container_width=True)
    submit_conversation = st.form_submit_button("Add Conversation")

    if submit_conversation and messages and selected_agent_cf:
        try:
            conversation_use_cases.create(selected_agent_cf.name, messages)
            st.success("Conversation added successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# Delete a conversation
st.subheader("Delete a conversation")


with st.form("Delete Conversation form"):
    conversation_id_to_delete = st.text_input("Insert Conversation ID").strip('"').strip("'")
    delete_conversation = st.form_submit_button("Delete Conversation")

    if delete_conversation and conversation_id_to_delete:
        try:
            conversation_use_cases.delete_by_id(conversation_id_to_delete)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
