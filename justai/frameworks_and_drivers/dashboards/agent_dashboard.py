import time
from typing import List
import pandas as pd
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer
from justai.entities.agent import Agent

from justai.use_cases.agent_use_cases import AgentUseCases

if "user" not in st.session_state:
    st.session_state.user = "None"
if "agent" not in st.session_state:
    st.session_state.agent = "None"


def display_agents(agents):
    # Markdown and dataframe display code goes here...
    agents_df = pd.json_normalize([agent.to_dict() for agent in agents])
    filtered_agents_df = dataframe_explorer(agents_df, case=False)
    st.dataframe(filtered_agents_df)


def create_new_agent(agent_use_cases: AgentUseCases):
    with st.form("Create Agent form"):
        agent_name = st.text_input("Enter agent name")
<<<<<<< HEAD
        system_prompt = st.text_input("Enter system prompt for agent")
=======
        system_prompt = st.text_area("Enter system prompt for agent")
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
        submit_agent = st.form_submit_button("Create Agent")

        if submit_agent and agent_name and system_prompt:
            try:
                agent_use_cases.create(agent_name, system_prompt)
                st.session_state.agent = agent_name
                st.success(f"Agent {agent_name} created successfully!")
                time.sleep(3)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def remove_agent(agent_use_cases: AgentUseCases, agent_names: List[str]):
<<<<<<< HEAD
    try:
        default_index = agent_names.index(st.session_state.agent)
    except ValueError:
        default_index = 0  # or another default value like None
    with st.form("Remove Agent form"):
        selected_agent_name = st.selectbox(
            "Select Agent to Remove",
            agent_names,
            index=default_index
=======
    with st.form("Remove Agent form"):
        selected_agent_name = st.selectbox(
            "Select Agent to Remove",
            agent_names
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
        )
        delete_agent = st.form_submit_button("Remove Agent")

        if delete_agent and selected_agent_name:
            try:
                agent_use_cases.delete(selected_agent_name)
                st.success(f"Agent {selected_agent_name} removed successfully!")
                time.sleep(3)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def update_agent_details(agent_use_cases: AgentUseCases, agent_names: List[str]):
<<<<<<< HEAD
    try:
        default_index = agent_names.index(st.session_state.agent)
    except ValueError:
        default_index = 0  # or another default value like None
    selected_agent_name = st.selectbox(
        "Choose an agent to update its details.",
        agent_names,
        index=default_index
=======
    selected_agent_name = st.selectbox(
        "Choose an agent to update its details.",
        agent_names
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
    )
    st.session_state.agent = selected_agent_name
    current_system_prompt = None
    if selected_agent_name:
        current_system_prompt = agent_use_cases.get_one(selected_agent_name).system_prompt
    else:
        st.warning("No agent to modify")

    with st.form("Update Agent form"):
        new_agent_name = st.text_input(
            "Enter the updated name for the selected agent.",
            value=selected_agent_name or "None"
        )
<<<<<<< HEAD
        new_system_prompt = st.text_input(
=======
        new_system_prompt = st.text_area(
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
            "Modify the system prompt.\
            The text for initial guidance or starter text for engaging with the selected agent.",
            value=current_system_prompt or ""
        )
        modify_agent = st.form_submit_button("Update Agent")
        if modify_agent and not (new_system_prompt):
            st.warning("Please fill in the new system prompt")
        if modify_agent and selected_agent_name and new_agent_name and new_system_prompt:
            try:
                agent_use_cases.edit(selected_agent_name, new_agent_name, new_system_prompt)
                st.session_state.agent = new_agent_name
                st.success(f"Agent {selected_agent_name} updated successfully!")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def agent_management_dashboard(agent_use_cases: AgentUseCases, agents: List[Agent], expander=False):
    st.header("Agent Management Dashboard")
    st.subheader("Agent Directory")
    agent_column_headers = '''
    - **ID**: Unique identifier assigned to each agent.
    - **Agent Name**: Distinctive name given to the agent for identification.
    - **System Prompt**: Initial guidance or starter text to engage with each agent.
    - **Dataset Generation Prompts**: Predefined prompts utilized to generate synthetic conversations.'''
    st.caption("Presented below is a comprehensive list of agents developed by the JustAI team.\
        These agents symbolize entities within our databases.\
        Coupled with ample 'Conversation' data housed in a separate directory,\
        JustAI is equipped to train specialized large language models that drive the capabilities of these agents.")
    if expander:
        st.markdown("**Column Headers:**")
        st.markdown(agent_column_headers)
    else:
        with st.expander("Column Headers:"):
            st.markdown(agent_column_headers)
    display_agents(agents)
    st.subheader("Create a New Agent")
    st.caption("Add a new agent by entering the agent's name and providing a system prompt.")
    create_new_agent(agent_use_cases)
    st.subheader("Remove an agent")
    st.caption("Select an agent from the dropdown menu to remove it from the system.")
    remove_agent(agent_use_cases, [agent.name for agent in agents])
    st.subheader("Update an agent's details")
    st.caption("Select an agent from the dropdown menu and enter a new system prompt to update the agent's details.")
    update_agent_details(agent_use_cases, [agent.name for agent in agents])
