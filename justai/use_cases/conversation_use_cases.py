from typing import Dict, List

from justai.application.exceptions import NotFoundError
from justai.entities.conversation import Conversation
from justai.interface_adapters.conversational_repository_interface import IBackupRepository, IConversationRepository
from justai.interface_adapters.conversational_repository_interface import IAgentRepository


class ConversationUseCases:
    def __init__(self,
                 agent_repository: IAgentRepository,
                 conversation_repository: IConversationRepository,
                 backup_repository: IBackupRepository):
        self.agent_repository = agent_repository
        self.conversation_repository = conversation_repository
        self.backup_repository = backup_repository

    def create(self, agent_name: str, messages: List[Dict[str, str]]) -> None:
        agent = self.agent_repository.get_by_name(agent_name)
        if not agent:
            raise NotFoundError(f"No agent found with the name {agent_name}.")
        conversation = Conversation(agent_name, messages)
        self.conversation_repository.create(conversation)

    def get_all(self) -> List[Conversation]:
        return self.conversation_repository.get_all()

    def get_by_agent_name(self, agent_name: str) -> List[Conversation]:
        return self.conversation_repository.get_by_agent_name(agent_name)

    def delete_by_id(self, conversation_id: str) -> None:
        # First backup the conversation
        conversation = self.conversation_repository.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundError(f"No conversation found with the ID {conversation_id}.")
        self.backup_repository.backup_conversations(conversation)
        self.conversation_repository.delete_by_id(conversation_id)

    def modify(self, conversation_id: str, new_messages: List[Dict[str, str]]) -> None:
        conversation_to_edit = self.conversation_repository.get_by_id(conversation_id)
        if not conversation_to_edit:
            raise NotFoundError(f"No conversation found with the ID {conversation_id}.")
        edited_conversation = Conversation(conversation_to_edit.agent_name, new_messages)
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
