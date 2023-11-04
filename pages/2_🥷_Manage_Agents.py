import streamlit as st

import justai
from justai.frameworks_and_drivers.dashboards.agent_dashboard import agent_management_dashboard
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases

st.set_page_config(layout="wide")

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

####
# AGENTS
####
agents = agent_use_cases.get_all()
agent_names = [agent.name for agent in agents]

agent_management_dashboard(agent_use_cases, agents)
