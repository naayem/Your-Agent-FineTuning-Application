from abc import ABC, abstractmethod
from typing import List, Optional, Union
from justai.entities.agent import Agent
from justai.entities.conversation import Conversation


class IAgentRepository(ABC):
    """
    An interface for managing agents in the storage layer.

    Methods:
    - get_by_name(agent_name: str) -> Optional[Agent]: Fetch an agent by its name.
    - create(agent: Agent) -> None: Create a new agent.
    - update(current_agent: Agent, updated_agent: Agent) -> None: Update an existing agent.
    - delete(agent: Agent) -> None: Delete an agent.
    - get_all() -> List[Agent]: Fetch all agents.

    Implementing classes should ensure these methods are provided with appropriate
    storage-level logic to handle agent data.
    """

    @abstractmethod
    def get_by_name(self, agent_name: str) -> Optional[Agent]:
        """Fetch an agent by its name."""
        pass

    @abstractmethod
    def create(self, agent: Agent) -> None:
        """Create a new agent."""
        pass

    @abstractmethod
    def update(self, current_agent: Agent, updated_agent: Agent) -> None:
        """Update an existing agent."""
        pass

    @abstractmethod
    def delete(self, agent: Agent) -> None:
        """Delete an agent."""
        pass

    @abstractmethod
    def get_all(self) -> List[Agent]:
        """Fetch all agents."""
        pass


class IConversationRepository(ABC):
    """
    An interface for managing conversations in the storage layer.

    Methods:
    - create(conversation: Conversation) -> None: Create a new conversation.
    - get_by_agent_name(agent_name: str) -> List[Conversation]:
        Fetch conversations linked with a specific agent by name.
    - get_by_id(conversation_id: str) -> Conversation: Fetch a conversation by its ID.
    - update_agent_field(current_agent: Agent, updated_agent: Agent) -> None:
        Update agent details in linked conversations.
    - delete_by_agent_name(agent_name: str) -> None: Delete conversations linked with a specific agent by name.
    - delete_by_agent_object(agent: Agent) -> None: Delete conversations linked with a specific agent object.
    - recover(conversations: List) -> None: Recover a list of conversations from backup.
    - get_all() -> List[Conversation]: Fetch all conversations.

    Concrete implementations should provide the above methods to handle conversations and their associations with agents
    """

    @abstractmethod
    def create(self, conversation: Conversation) -> None:
        """Create a new conversation."""
        pass

    @abstractmethod
    def get_by_agent_name(self, agent_name: str) -> List[Conversation]:
        """Fetch conversations linked with a specific agent."""
        pass

    @abstractmethod
    def get_by_id(self, conversation_id: str) -> Conversation:
        """Fetch conversations linked with a specific agent."""
        pass

    @abstractmethod
    def update_agent_field(self, current_agent: Agent, updated_agent: Agent) -> None:
        """Update agent details in linked conversations."""
        pass

    @abstractmethod
    def update(self, current_conversation: Conversation, updated_conversation: Conversation) -> None:
        """Update an existing conversation."""
        pass

    @abstractmethod
    def delete_by_agent_name(self, agent_name: str) -> None:
        """Delete all conversations linked with a specific agent."""
        pass

    @abstractmethod
    def delete_by_agent_object(self, agent: Agent) -> None:
        """Delete all conversations linked with a specific agent object."""
        pass

    @abstractmethod
    def delete_by_id(self, conversation_id: str) -> None:
        """Delete a conversation by its ID."""
        pass

    @abstractmethod
    def recover(self, conversations: List) -> None:
        """Recover a list of conversations from backup."""
        pass

    @abstractmethod
    def get_all(self) -> List[Conversation]:
        """Fetch all conversations."""
        pass


class IBackupRepository(ABC):
    """
    An interface for backing up and retrieving conversations.

    Methods:
    - backup_conversations(conversations: Union[List[Conversation], Conversation]) -> None: Backup a list conversations.
    - get_conversations_by_agent_object(agent: Agent) -> List: Fetch convos linked with a specific agent from backup.
    - delete_conversations_by_agent_object(agent: Agent) -> None: Delete convos linked with specific agent from backup.

    Implementing classes should manage the backups efficiently and ensure retrieval and deletions are accurate.
    """

    @abstractmethod
    def backup_conversations(self, conversations: Union[List[Conversation], Conversation]) -> None:
        """Backup a list of conversations."""
        pass

    @abstractmethod
    def get_conversations_by_agent_object(self, agent: Agent) -> List:
        """Fetch conversations linked with a specific agent from backup."""
        pass

    @abstractmethod
    def delete_conversations_by_agent_object(self, agent: Agent) -> None:
        """Delete conversations linked with a specific agent from backup."""
        pass
