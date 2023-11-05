from typing import List, Optional
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from justai.entities.feedback import Feedback, FeedbackTag
from justai.interface_adapters.feedback_repository_interface import IFeedbackRepository


class MongoFeedbackRepository(IFeedbackRepository):
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client["FeedbackDB"]
        self.collection = self.db['feedback']

    def create(self, feedback: Feedback) -> None:
        try:
            self.collection.insert_one(feedback.serialize())
        except DuplicateKeyError:
            raise ValueError(f"Feedback with id {feedback.id} already exists.")

    def get_by_id(self, feedback_id: int) -> Optional[Feedback]:
        document = self.collection.find_one({"id": feedback_id})
        if document:
            return Feedback(
                label=document["label"],
                user_name=document["user_name"],
                content=document["content"],
                tags=[FeedbackTag(tag) for tag in document["tags"]],
                rating=document["rating"],
                created_at=document["created_at"],
                id=document["id"]
            )
        return None

    def update(self, current_feedback: Feedback, updated_feedback: Feedback) -> None:
        self.collection.update_one(
            {"id": current_feedback.id},
            {"$set": updated_feedback.serialize()}
        )

    def delete(self, feedback: Feedback) -> None:
        self.collection.delete_one({"id": feedback.id})

    def get_all(self) -> List[Feedback]:
        cursor = self.collection.find()
        return [
            Feedback(
                label=doc["label"],
                user_name=doc["user_name"],
                content=doc["content"],
                tags=[FeedbackTag(tag) for tag in doc["tags"]],
                rating=doc["rating"],
                created_at=doc["created_at"],
                id=doc["id"]
            ) for doc in cursor
        ]
