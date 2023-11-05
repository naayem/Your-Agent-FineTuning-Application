from enum import Enum, unique
import datetime


@unique
class FeedbackTag(Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    USER_EXPERIENCE = "user_experience"
    PERFORMANCE = "performance"
    SECURITY = "security"
    OTHER = "other"


class Feedback:
    def __init__(
        self,
        label: str,
        user_name: str,
        content: str,
        tags: list[FeedbackTag],
        rating: int,
        created_at: datetime.datetime,
        id: int = None  # id is optional and will be assigned by the database
    ):
        self.id = id  # Unique identifier for the feedback
        self.label = label  # Label of the feedback (e.g., "positive", "negative", "neutral")
        self.user_name = user_name  # Name of the user who provided the feedback
        self.content = content  # The content of the feedback
        self.tags = tags  # Tags associated with the feedback, using FeedbackTag enumeration
        self.rating = rating  # Rating associated with the feedback (e.g., 1-5)
        self.created_at = created_at  # Timestamp when the feedback was created

    def __repr__(self):
        return f"<Feedback {self.id if self.id else 'unsaved'}>"

    def serialize(self):
        # Convert to datetime if 'created_at' is a string
        if isinstance(self.created_at, str):
            # Assume the string is in a known format, e.g., 'YYYY-MM-DDTHH:MM:SS'
            # You will need to adjust the format to match what you're actually using
            created_at = datetime.datetime.fromisoformat(self.created_at)
        else:
            created_at = self.created_at

        return {
            'id': self.id,
            'label': self.label,
            'user_name': self.user_name,
            'content': self.content,
            'tags': [tag.value for tag in self.tags],
            'rating': self.rating,
            'created_at': created_at.isoformat() if created_at else None
        }
