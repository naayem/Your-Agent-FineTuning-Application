from typing import List, Dict, Optional


class Message:
    """
    Represents a message in a conversation.

    Attributes:
        role (str): The role (e.g., "user", "agent") of the sender of the message.
        content (str): The actual text content of the message.

    Methods:
        to_dict: Returns a dictionary representation of the Message object.
    """
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

    def __repr__(self) -> str:
        return f"Message(role={self.role}, content={self.content})"


class Conversation:
    """
    Represents a conversation which consists of a list of messages.

    Attributes:
        agent_name (str): The name or title of the conversation.
        messages (List[Message]): A list of messages that form the conversation.
        id (Optional[str]): An optional identifier for the conversation.

    Methods:
        to_dict: Returns a dictionary representation of the Conversation object.
    """
    def __init__(self, name: str, messages: List[Message], id: Optional[str] = None):
        self.agent_name = name
        self.messages = messages
        self.id = id or None

    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            "id": self.id or "",
            "agent_name": self.agent_name,
            "messages": [message.to_dict() for message in self.messages]
        }

    def to_dict_stringify_messages(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            "id": self.id or "",
            "agent_name": self.agent_name,
            "messages": [message.__repr__() for message in self.messages]
        }

    def __repr__(self) -> str:
        return f"Conversation(agent_name={self.agent_name}, messages={self.messages}, id={self.id})"
