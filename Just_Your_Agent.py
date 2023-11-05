import streamlit as st
import justai
from justai.frameworks_and_drivers.dashboards.feedback_dashboard import FeedbackManagementDashboard
from justai.use_cases.agent_use_cases import AgentUseCases
from justai.use_cases.conversation_use_cases import ConversationUseCases
from justai.use_cases.feedback_use_cases import FeedbackUseCases
from justai.use_cases.user_use_cases import UserUseCases

import locale

locale.getpreferredencoding = lambda: "UTF-8"

# App title
st.set_page_config(page_title="JAW OpenAI FineTuning 👁️", layout="wide")

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
# Home Page
########################################################################################################################

st.title('JAW OpenAI Spinning Off Agents 👁️')
st.header('This is my home page I have to be creative here')
st.write("Let's show a dashboard of the current openAI jobs and let's maybe have a readme home page")

# Fetch list of all users for authentication
users = user_use_cases.get_all()
user_names = [user.user_name for user in users]

try:
    default_index = user_names.index(st.session_state.user)
except ValueError:
    default_index = 0  # or another default value like None
# User authentication
st.session_state.user = st.selectbox(
    "Please select your username:",
    user_names,
    index=default_index,
    format_func=str
)

# Display welcome message after authentication
if st.session_state.user:
    st.write(f"Welcome, {st.session_state.user}!")

# Fetch list of all users for authentication
agents = agent_use_cases.get_all()
agent_names = [agent.name for agent in agents]

try:
    default_index = agent_names.index(st.session_state.agent)
except ValueError:
    default_index = 0  # or another default value like None
# Agent Selection
st.session_state.agent = st.selectbox(
    "Select an agent to work with:",
    agent_names,
    index=default_index,
    format_func=str
)

# Display ready message after agent selection
if st.session_state.user:
    st.write(f"{st.session_state.agent} is at your service!")

with st.sidebar:
    st.divider()
    with st.expander(":green[**Any Feedback?**]"):
        feedback_management_dashboard.create_new_feedback()