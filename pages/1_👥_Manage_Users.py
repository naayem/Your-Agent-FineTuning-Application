import streamlit as st
import justai
from justai.frameworks_and_drivers.dashboards.feedback_dashboard import FeedbackManagementDashboard
from justai.frameworks_and_drivers.dashboards.user_dashboard import UserManagementDashboard
from justai.use_cases.feedback_use_cases import FeedbackUseCases
from justai.use_cases.user_use_cases import UserUseCases

st.set_page_config(layout="wide")

# Sidebar for database connection configuration
st.sidebar.header("Configuration")
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()
if not repos:
    st.sidebar.warning("Configure the database connection here before proceeding.")

user_use_cases = UserUseCases(repos["user"])
feedback_use_cases = FeedbackUseCases(repos["feedback"])
feedback_management_dashboard = FeedbackManagementDashboard(feedback_use_cases, user_use_cases)


user_management_dashboard = UserManagementDashboard(user_use_cases)
user_management_dashboard.render()

st.divider()
with st.expander(":green[**Any Feedback?**]"):
    feedback_management_dashboard.create_new_feedback()
