import time
import pandas as pd
import streamlit as st
from datetime import datetime
from justai.frameworks_and_drivers.dashboards.extra_dataframe_explorer import dataframe_explorer
from justai.use_cases.feedback_use_cases import FeedbackUseCases
from justai.entities.feedback import FeedbackTag
from justai.use_cases.user_use_cases import UserUseCases


class FeedbackManagementDashboard:
    def __init__(self, feedback_use_cases: FeedbackUseCases, user_use_cases: UserUseCases):
        self.feedback_use_cases = feedback_use_cases
        self.user_use_cases = user_use_cases
        if "feedback" not in st.session_state:
            st.session_state.feedback = None

    def display_feedbacks(self):
        feedbacks = self.feedback_use_cases.get_all()
        feedbacks_df = pd.DataFrame([feedback.serialize() for feedback in feedbacks])
        filtered_feedbacks_df = dataframe_explorer(feedbacks_df, case=False)
        st.dataframe(filtered_feedbacks_df, use_container_width=True)

    def create_new_feedback(self):
        user_names = [user.user_name for user in self.user_use_cases.get_all()]
        with st.form("Create Feedback form"):
            label = st.text_input("Feedback Label")
            user_name = st.selectbox("User Name", user_names)
            content = st.text_area("Feedback Content")
            tags = st.multiselect("Feedback Tags", [tag.value for tag in FeedbackTag])
            rating = st.slider("Rating", 1, 5, 3)
            add_feedback = st.form_submit_button("Submit Feedback")
            if add_feedback and user_name and content:
                try:
                    self.feedback_use_cases.create(
                        label, user_name, content,
                        [FeedbackTag(tag) for tag in tags], rating, datetime.now()
                    )
                    st.success(f"Feedback from '{user_name}' has been added successfully.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Submission failed: {e}")

    def delete_feedback(self):
        feedbacks = self.feedback_use_cases.get_all()
<<<<<<< HEAD
        feedback_ids = [feedback.id for feedback in feedbacks]
        feedback_id_to_delete = st.selectbox("Choose Feedback to Remove", feedback_ids)
        if st.button("Delete Feedback"):
            try:
                self.feedback_use_cases.delete(feedback_id_to_delete)
                st.success(f"Feedback with ID '{feedback_id_to_delete}' has been removed successfully.")
=======
        feedback_labels = [feedback.label for feedback in feedbacks]
        feedback_label_to_delete = st.selectbox("Choose Feedback to Remove", feedback_labels)
        if st.button("Delete Feedback"):
            try:
                self.feedback_use_cases.delete(feedback_label_to_delete)
                st.success(f"Feedback with label '{feedback_label_to_delete}' has been removed successfully.")
>>>>>>> c6a8f0f (Remove unused files and update dependencies)
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Removal failed: {e}")

    def render(self):
        st.title("Feedback Management Dashboard")

        st.header("Feedback Directory")
        st.caption("Browse through all the feedback entries.")
        self.display_feedbacks()

        st.header("Submit New Feedback")
        st.caption("Add a new feedback entry to the system.")
        self.create_new_feedback()

        st.header("Delete Feedback")
        st.caption("Remove an existing feedback entry.")
        self.delete_feedback()

# Assume that feedback_use_cases is an instance of FeedbackUseCases
# feedback_management_dashboard = FeedbackManagementDashboard(feedback_use_cases)
# feedback_management_dashboard.render()
