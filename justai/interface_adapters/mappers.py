# mappers.py or factories.py in the application layer

from typing import Dict, List
from justai.entities.conversation import Conversation, Message


def map_to_conversation(session_messages: List[Dict[str, str]], agent_name: str) -> Conversation:
    """
    Maps a list of messages from the session state to a Conversation entity.

    Args:
    - session_messages (List[Dict[str, str]]): A list of messages with role and content.
    - agent_name (str): The name of the agent participating in the conversation.

    Returns:
    - Conversation: A Conversation entity.
    """

    # Convert each dictionary to a Message object
    message_objects = [Message(msg["role"], msg["content"]) for msg in session_messages]
    assistant_message = [Message("assistant", "")]

    # Return a Conversation object using the list of Message objects
    return Conversation(agent_name, assistant_message + message_objects)
