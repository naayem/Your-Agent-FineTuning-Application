import streamlit as st
import justai
from justai.frameworks_and_drivers.dashboards.user_dashboard import user_management_dashboard
from justai.use_cases.user_use_cases import UserUseCases

st.set_page_config(layout="wide")

# Sidebar for database connection configuration
st.sidebar.header("Configuration")
repos = justai.frameworks_and_drivers.database_sidebar.database_sidebar()
if not repos:
    st.sidebar.warning("Configure the database connection here before proceeding.")

user_use_cases = UserUseCases(repos["user"])

user_management_dashboard(user_use_cases)
