import datetime
from typing import List
from justai.application.exceptions import NotFoundError
from justai.entities.feedback import Feedback, FeedbackTag
from justai.interface_adapters.feedback_repository_interface import IFeedbackRepository


class FeedbackUseCases:
    def __init__(self, feedback_repository: IFeedbackRepository):
        self.feedback_repository = feedback_repository

    def create(
        self,
        label: str,
        user_name: str,
        content: str,
        tags: List[FeedbackTag],
        rating: int,
        created_at: datetime.datetime = datetime.datetime.now()
    ) -> None:
        """
        Creates a new feedback entry in the database.

        Args:
            label (str): The label of the feedback.
            user_name (str): The name of the user who provided the feedback.
            content (str): The content of the feedback.
            tags (List[FeedbackTag]): The tags associated with the feedback.
            rating (int): The rating associated with the feedback.
            created_at (datetime.datetime): The timestamp when the feedback was created.
        """
        feedback = Feedback(label, user_name, content, tags, rating, created_at)
        self.feedback_repository.create(feedback)

    def get_all(self) -> List[Feedback]:
        """Returns a list of all feedback entries."""
        return self.feedback_repository.get_all()

    def get(self, feedback_id: int) -> Feedback:
        """
        Returns a feedback object.

        Args:
            feedback_id (int): The ID of the feedback to retrieve.

        Raises:
            NotFoundError: If the feedback with the given ID is not found.
        """
        feedback = self.feedback_repository.get_by_id(feedback_id)
        if not feedback:
            raise NotFoundError(f"Feedback with the ID {feedback_id} not found.")
        return feedback

    def delete(self, feedback_id: int) -> None:
        """
        Deletes a feedback entry from the database.

        Args:
            feedback_id (int): The ID of the feedback to delete.

        Raises:
            NotFoundError: If the feedback with the given ID is not found.
        """
        feedback = self.get(feedback_id)  # Reuse the get method for validation
        self.feedback_repository.delete(feedback)

    def edit(
        self,
        feedback_id: int,
        new_label: str,
        new_content: str,
        new_tags: List[FeedbackTag],
        new_rating: int
    ) -> None:
        """
        Edits an existing feedback entry.

        Args:
            feedback_id (int): The ID of the feedback to edit.
            new_label (str): The new label for the feedback.
            new_content (str): The new content of the feedback.
            new_tags (List[FeedbackTag]): The new tags for the feedback.
            new_rating (int): The new rating for the feedback.

        Raises:
            NotFoundError: If the feedback with the given ID is not found.
        """
        feedback_to_edit = self.get(feedback_id)  # Reuse the get method for validation
        updated_feedback = Feedback(
            new_label,
            feedback_to_edit.user_name,
            new_content,
            new_tags,
            new_rating,
            feedback_to_edit.created_at,
            id=feedback_id
        )
        self.feedback_repository.update(feedback_to_edit, updated_feedback)
