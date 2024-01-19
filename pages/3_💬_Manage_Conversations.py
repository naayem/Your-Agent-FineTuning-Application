import streamlit as st

import justai
from justai.frameworks_and_drivers.dashboards.agent_dashboard import agent_management_dashboard
from justai.frameworks_and_drivers.dashboards.conversation_dashboard import conversation_management_dashboard
from justai.frameworks_and_drivers.dashboards.feedback_dashboard import FeedbackManagementDashboard
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases
from justai.use_cases.feedback_use_cases import FeedbackUseCases
from justai.use_cases.user_use_cases import UserUseCases

st.set_page_config(layout="wide")

if "user" not in st.session_state:
    st.session_state.user = "None"
if "agent" not in st.session_state:
    st.session_state.agent = "None"

########################################################################################################################
# SIDEBAR
########################################################################################################################
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()

if not repos:
    st.warning("Please configure the database connection first.")

agent_use_cases = AgentUseCases(repos["agent"], repos["backup"], repos["conversation"])
conversation_use_cases = ConversationUseCases(repos["agent"], repos["conversation"], repos["backup"])
user_use_cases = UserUseCases(repos["user"])
feedback_use_cases = FeedbackUseCases(repos["feedback"])
feedback_management_dashboard = FeedbackManagementDashboard(feedback_use_cases, user_use_cases)
########################################################################################################################
# CRUD
########################################################################################################################

####
# AGENTS
####
agents = agent_use_cases.get_all()
agent_names = [agent.name for agent in agents]

with st.expander("Agent Management Dashboard"):
    agent_management_dashboard(agent_use_cases, agents, expander=True)

####
# CONVERSATIONS
####
all_conversations = conversation_use_cases.get_all()

conversation_management_dashboard(
    agent_use_cases,
    conversation_use_cases,
    [agent.name for agent in agents],
    all_conversations
)

st.divider()
with st.expander(":green[**Any Feedback?**]"):
    feedback_management_dashboard.create_new_feedback()
