from typing import Dict, List, Optional

from justai.application.exceptions import NotFoundError
from justai.entities.conversation import Conversation
from justai.interface_adapters.conversational_repository_interface import IBackupRepository, IConversationRepository
from justai.interface_adapters.conversational_repository_interface import IAgentRepository


class ConversationUseCases:
    """
    Provides use cases for managing conversations.

    Attributes:
        agent_repository (IAgentRepository): Repository for accessing agent data.
        conversation_repository (IConversationRepository): Repository for accessing conversation data.
        backup_repository (IBackupRepository): Repository for accessing backup data of conversations.

    Methods:
        create: Adds a new conversation to the repository.
        get_all: Retrieves all conversations from the repository.
        get_by_agent_name: Retrieves all conversations associated with a specific agent.
        delete_by_id: Deletes a conversation by its ID and backs it up before deletion.
        modify_messages: Updates the messages of a conversation.
        modify: Updates messages, ID, and tags of a conversation.
        recover: Recovers a backed-up conversation by its ID and deletes the backup afterwards.
        search_in_conversations_by_tag: Filters a list of conversations by a specific tag.
        search_in_conversations_by_agent_name: Filters a list of conversations by a specific agent name.
    """
    def __init__(self,
                 agent_repository: IAgentRepository,
                 conversation_repository: IConversationRepository,
                 backup_repository: IBackupRepository):
        self.agent_repository = agent_repository
        self.conversation_repository = conversation_repository
        self.backup_repository = backup_repository

    def create(
        self,
        agent_name: str,
        messages: List[Dict[str, str]],
        id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Conversation:
        id = id or None
        tags = tags or None
        agent = self.agent_repository.get_by_name(agent_name)
        if not agent:
            raise NotFoundError(f"No agent found with the name {agent_name}.")
        conversation = Conversation(agent_name, messages, id, tags)
        self.conversation_repository.create(conversation)
        return conversation

    def get_all(self) -> List[Conversation]:
        return self.conversation_repository.get_all()

    def get_by_agent_name(self, agent_name: str) -> List[Conversation]:
        return self.conversation_repository.get_by_agent_name(agent_name)

    def delete_by_id(self, conversation_id: str) -> Conversation:
        # First backup the conversation
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundError(f"No conversation found with the ID {conversation_id}.")
        self.backup_repository.backup_conversations(conversation)
        self.conversation_repository.delete_by_id(conversation_id)
        return conversation

    def modify_messages(self, conversation_id: str, new_messages: List[Dict[str, str]]) -> None:
        conversation_to_edit = self.conversation_repository.get_by_id(conversation_id)
        if not conversation_to_edit:
            raise NotFoundError(f"No conversation found with the ID {conversation_id}.")
        edited_conversation = Conversation(conversation_to_edit.agent_name, new_messages)
        self.conversation_repository.update(conversation_to_edit, edited_conversation)

    def modify(
        self,
        conversation_id: str,
        new_messages: List[Dict[str, str]],
        id: Optional[str],
        tags: Optional[List[str]]
    ) -> None:
        id = id or None
        tags = tags or None
        conversation_to_edit = self.conversation_repository.get_by_id(conversation_id)
        if not conversation_to_edit:
            raise NotFoundError(f"No conversation found with the ID {conversation_id}.")
        edited_conversation = Conversation(conversation_to_edit.agent_name, new_messages, id, tags)
        self.conversation_repository.update(conversation_to_edit, edited_conversation)

    def recover(self, conversation_id: str) -> None:
        '''
        NOT IMPLEMENTED
        '''
        backed_up_conversation = self.backup_repository.get_by_id(conversation_id)
        if not backed_up_conversation:
            raise NotFoundError(f"No backup found for the conversation with ID {conversation_id}.")
        self.conversation_repository.create(backed_up_conversation)
        # Once recovered, remove the backed up conversation
        self.backup_repository.delete_by_id(conversation_id)

    def search_in_conversations_by_tag(self, conversations: List[Conversation], tag: str) -> List[Conversation]:
        return [conversation for conversation in conversations if tag in conversation.tags]

    def search_in_conversations_by_agent_name(
        self,
        conversations: List[Conversation],
        agent_name: str
    ) -> List[Conversation]:
        return [conversation for conversation in conversations if agent_name == conversation.agent_name]

    def extract_labels_from_conversations(self, conversations: List[Conversation]) -> Dict[str, Conversation]:
        """
        Extract labels from conversations based on the 'label: ' prefix in tags.

        Args:
            conversations (List[Conversation]): A list of Conversation objects.

        Returns:
            Dict[str, Conversation]: A dictionary mapping conversation objects to their corresponding labels.
        """
        label_dict = {}

        for convo in conversations:
            for tag in convo.tags:
                if tag.startswith("label: "):
                    label_dict[tag.replace("label: ", "").strip()] = convo
                    break  # Assuming there's only one label per conversation

        return label_dict

    def overwrite(self, conversation: Conversation, label: str):
        """
        Overwrites the conversation with the same ID in the repository.
        """
        try:
            # Try to get the conversation
            existing_conversation = self.conversation_repository.get_by_id(conversation.id)

            # If the conversation exists, update its tags
            if existing_conversation:

                # Retrieve existing tags
                existing_tags = conversation.tags

                # Update label in tags
                updated_tags = [tag for tag in existing_tags if not tag.startswith("label: ")]
                updated_tags.append(label)

                # Update the tags of the conversation object
                conversation.tags = updated_tags

                # Overwrite the existing conversation
                self.conversation_repository.update(existing_conversation, conversation)

        except ValueError:
            # Handle the error raised when the conversation doesn't exist
            raise (f"Conversation with id {conversation.id} does not exist. Will not create a new one.")

    def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieves a conversation by its ID.

        Args:
            conversation_id (str): The ID of the conversation to retrieve.

        Returns:
            Conversation: The conversation object if found; otherwise, None.

        Raises:
            NotFoundError: If no conversation is found with the given ID.
        """
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundError(f"No conversation found with the ID {conversation_id}.")
        return conversation
