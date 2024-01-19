from typing import List, Optional, Union

from bson import ObjectId
from justai.entities.agent import Agent
from justai.entities.conversation import Conversation, Message
from justai.entities.user import User
from justai.interface_adapters.conversational_repository_interface import IAgentRepository, IUserRepository
from justai.interface_adapters.conversational_repository_interface import IBackupRepository
from justai.interface_adapters.conversational_repository_interface import IConversationRepository


from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoUserRepository(IUserRepository):
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client["AgentConvoDB"]
        self.collection = self.db['user']

    def get_by_name(self, user_name: str) -> Optional[User]:
        document = self.collection.find_one({"user_name": user_name})
        if document:
            return User(document["user_name"])
        return None

    def create(self, user: User) -> None:
        try:
            self.collection.insert_one(
                {
                    "user_name": user.user_name
                }
            )
        except DuplicateKeyError:
            raise ValueError(f"User with name {user.user_name} already exists.")

    def update(self, current_user: User, updated_user: User) -> None:
        self.collection.update_one(
            {
                "user_name": current_user.user_name
            },
            {
                "$set": {
                    "user_name": updated_user.user_name
                }
            }
        )

    def delete(self, user: User) -> None:
        self.collection.delete_one({"user_name": user.user_name})

    def get_all(self) -> List[User]:
        cursor = self.collection.find()
        return [User(doc["user_name"]) for doc in cursor]


class MongoAgentRepository(IAgentRepository):
    def __init__(self, uri: str):
        self.client = MongoClient(uri)
        self.db = self.client["AgentConvoDB"]
        self.collection = self.db['agent']

    def get_by_name(self, agent_name: str) -> Optional[Agent]:
        document = self.collection.find_one({"name": agent_name})
        if document:
            return Agent(document["name"], document["system_prompt"], document["dataset_generation_prompts"])
        return None

    def create(self, agent: Agent) -> None:
        try:
            self.collection.insert_one(
                {
                    "name": agent.name,
                    "system_prompt": agent.system_prompt,
                    "dataset_generation_prompts": agent.dataset_generation_prompts
                }
            )
        except DuplicateKeyError:
            raise ValueError(f"Agent with name {agent.name} already exists.")

    def update(self, current_agent: Agent, updated_agent: Agent) -> None:
        self.collection.update_one(
            {
                "name": current_agent.name
            },
            {
                "$set": {
                    "name": updated_agent.name,
                    "system_prompt": updated_agent.system_prompt,
                    "dataset_generation_prompts": updated_agent.dataset_generation_prompts
                }
            }
        )

    def delete(self, agent: Agent) -> None:
        self.collection.delete_one({"name": agent.name})

    def get_all(self) -> List[Agent]:
        cursor = self.collection.find()
        return [Agent(doc["name"], doc["system_prompt"], doc["dataset_generation_prompts"]) for doc in cursor]


class MongoConversationRepository(IConversationRepository):

    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client["AgentConvoDB"]
        self.collection = self.db["conversation"]

    def create(self, conversation: Conversation) -> None:
        if conversation.id:
            if self.collection.find_one({"id": conversation.id}):
                raise ValueError(f"Conversation with id {conversation.id} already exists.")
            self.collection.insert_one(
                {
                    "_id": ObjectId(conversation.id),
                    "agent_name": conversation.agent_name,
                    "messages": conversation.messages,
                    "tags": conversation.tags
                    }
                )
        else:
            self.collection.insert_one(
                {
                    "agent_name": conversation.agent_name,
                    "messages": conversation.messages,
                    "tags": conversation.tags
                }
            )

    def get_by_agent_name(self, agent_name: str) -> List[Conversation]:
        cursor = self.collection.find({"agent_name": agent_name})

        conversations = []
        for doc in cursor:
            # Assuming the MongoDB document has a 'name', 'messages', and '_id' field
            agent_name = doc['agent_name']

            # Convert list of message dicts to list of Message objects
            messages = [Message(message_doc['role'], message_doc['content']) for message_doc in doc['messages']]

            # Use the MongoDB _id as the conversation id
            id = str(doc['_id'])

            if 'tags' in doc:
                tags = doc['tags']
            else:
                tags = []

            conversation = Conversation(agent_name, messages, id, tags)
            conversations.append(conversation)

        return conversations

    def update_agent_field(self, current_agent: Agent, updated_agent: Agent) -> None:
        self.collection.update_many(
            {"agent_name": current_agent.name},
            {"$set": {"agent_name": updated_agent.name, "messages.$[elem].content": updated_agent.system_prompt}},
            array_filters=[{"elem.role": "system"}]
        )

    def delete_by_agent_name(self, agent_name: str) -> None:
        self.collection.delete_many({"agent_name": agent_name})

    def delete_by_agent_object(self, agent: Agent) -> None:
        self.collection.delete_many({"agent_name": agent.name, "agent_prompt": agent.system_prompt})

    def delete_by_id(self, conversation_id: str) -> None:
        self.collection.delete_one({"_id": ObjectId(conversation_id)})

    def recover(self, conversations: List) -> None:
        self.collection.insert_many(conversations)

    def get_all(self) -> List[Conversation]:
        cursor = self.collection.find()

        conversations = []
        for doc in cursor:
            # Assuming the MongoDB document has a 'name', 'messages', and '_id' field
            name = doc['agent_name']

            # Convert list of message dicts to list of Message objects
            messages = [Message(message_doc['role'], message_doc['content']) for message_doc in doc['messages']]

            # Use the MongoDB _id as the conversation id
            id = str(doc['_id'])

            if 'tags' in doc:
                tags = doc['tags']
            else:
                tags = []

            conversation = Conversation(name, messages, id, tags)
            conversations.append(conversation)

        return conversations

    def get_by_id(self, conversation_id: str) -> Conversation:
        document = self.collection.find_one(ObjectId(conversation_id))
        if document:
            messages = [Message(message_doc['role'], message_doc['content']) for message_doc in document['messages']]
            return Conversation(document["agent_name"], messages, document["_id"], document["tags"])
        else:
            raise ValueError(f"Conversation with id {conversation_id} does not exist.")

    def update(self, current_conversation: Conversation, updated_conversation: Conversation) -> None:
        '''
        Update a conversation in the database.
        updates the agent_name, messages, and tags fields.
        Do not update the id field
        '''
        self.collection.update_one(
            {"_id": current_conversation.id},
            {"$set": {
                "agent_name": updated_conversation.agent_name,
                "messages": [message.to_dict() for message in updated_conversation.messages],
                "tags": updated_conversation.tags
                }
             }
        )


class MongoBackupRepository(IBackupRepository):
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client["AgentConvoDB"]
        self.collection = self.db["backup"]

    def backup_conversations(self, conversations: Union[List[Conversation], Conversation]) -> None:
        """Backup a list of conversations."""
        # Assuming each conversation is a dictionary
        if isinstance(conversations, list):
            self.collection.insert_many([conversation.to_dict() for conversation in conversations])
        else:
            self.collection.insert_one(conversations.to_dict())

    def get_conversations_by_agent_object(self, agent: Agent) -> List:
        """Fetch conversations linked with a specific agent from backup."""
        return list(self.collection.find({"agent_name": agent.name}))

    def delete_conversations_by_agent_object(self, agent: Agent) -> None:
        """Delete conversations linked with a specific agent from backup."""
        self.collection.delete_many({"agent_name": agent.name})
