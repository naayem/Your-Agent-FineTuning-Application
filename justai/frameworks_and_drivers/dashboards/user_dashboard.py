import time
from typing import List
import pandas as pd
from justai.entities.user import User
from justai.use_cases.user_use_cases import UserUseCases

import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer

if "user" not in st.session_state:
    st.session_state.user = "None"


def display_users(user_use_cases: UserUseCases):
    users = user_use_cases.get_all()
    users_df = pd.json_normalize([user.to_dict() for user in users])
    filtered_users_df = dataframe_explorer(users_df, case=False)
    st.dataframe(filtered_users_df, width=400)


def create_new_user(user_use_cases: UserUseCases):
    with st.form("Create User form"):
        user_name = st.text_input("Enter User Name")
        add_user = st.form_submit_button("Register User")
        if add_user and user_name:
            try:
                user_use_cases.create(user_name)
                st.session_state.user = user_name
                st.success(f"User '{user_name}' has been added successfully.")
                time.sleep(3)
                st.rerun()
            except Exception as e:
                st.error(f"Registration failed: {e}")


def remove_user(user_use_cases: UserUseCases, users: List[User]):
    user_names = [user.user_name for user in users]
    try:
        default_index = user_names.index(st.session_state.user)
    except ValueError:
        default_index = 0  # or another default value like None
    with st.form("Remove User form"):
        selected_user_name_to_delete = st.selectbox(
            "Choose User to Remove",
            user_names,
            index=default_index,
            )
        delete_user = st.form_submit_button("Unregister User")
        if delete_user and selected_user_name_to_delete:
            try:
                user_use_cases.delete(selected_user_name_to_delete)
                st.success(f"User '{selected_user_name_to_delete}' has been removed successfully.")
                time.sleep(3)
                st.rerun()
            except Exception as e:
                st.error(f"Removal failed: {e}")


def update_user_details(user_use_cases: UserUseCases, users: List[User]):
    user_names = [user.user_name for user in users]
    try:
        default_index = user_names.index(st.session_state.user)
    except ValueError:
        default_index = 0  # or another default value like None
    selected_user_name = st.selectbox(
        "Choose User to Edit",
        user_names,
        index=default_index,
        )
    st.session_state.user = selected_user_name
    with st.form("Modify User form"):
        new_user_name = st.text_input("New User Name", value=selected_user_name or "")
        modify_user = st.form_submit_button("Update User")
        if modify_user and selected_user_name and new_user_name:
            try:
                user_use_cases.edit(selected_user_name, new_user_name)
                st.session_state.user = new_user_name
                st.success(f"User '{selected_user_name}' has been updated to '{new_user_name}'.")
                time.sleep(3)
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")


def user_management_dashboard(user_use_cases: UserUseCases):
    st.title("User Management Dashboard")

    st.header("User Directory")
    st.caption("A comprehensive list of all registered users.")
    display_users(user_use_cases)

    st.header("Register New User")
    st.caption("Create a new user profile.")
    create_new_user(user_use_cases)

    st.header("Unregister User")
    st.caption("Remove an existing user profile.")
    remove_user(user_use_cases, user_use_cases.get_all())

    st.header("Edit User Profile")
    st.caption("Update the details of an existing user profile.")
    update_user_details(user_use_cases, user_use_cases.get_all())
