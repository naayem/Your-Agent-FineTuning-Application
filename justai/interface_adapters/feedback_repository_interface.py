from typing import List, Optional
from abc import ABC, abstractmethod
from justai.entities.feedback import Feedback


class IFeedbackRepository(ABC):
    """
    An interface for managing feedback in the storage layer.

    Methods:
    - create(feedback: Feedback) -> None: Create a new feedback entry.
    - get_by_id(feedback_id: int) -> Optional[Feedback]: Fetch a feedback entry by its ID.
    - update(current_feedback: Feedback, updated_feedback: Feedback) -> None: Update an existing feedback entry.
    - delete(feedback: Feedback) -> None: Delete a feedback entry.
    - get_all() -> List[Feedback]: Fetch all feedback entries.

    Implementing classes should ensure these methods are provided with appropriate
    storage-level logic to handle feedback data.
    """

    @abstractmethod
    def create(self, feedback: Feedback) -> None:
        """Create a new feedback entry."""
        pass

    @abstractmethod
    def get_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """Fetch a feedback entry by its ID."""
        pass

    @abstractmethod
    def update(self, current_feedback: Feedback, updated_feedback: Feedback) -> None:
        """Update an existing feedback entry."""
        pass

    @abstractmethod
    def delete(self, feedback: Feedback) -> None:
        """Delete a feedback entry."""
        pass

    @abstractmethod
    def get_all(self) -> List[Feedback]:
        """Fetch all feedback entries."""
        pass
