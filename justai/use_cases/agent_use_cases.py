from justai.application.exceptions import DuplicateError, NotFoundError
from justai.entities.agent import Agent
from justai.interface_adapters.conversational_repository_interface import IAgentRepository
from justai.interface_adapters.conversational_repository_interface import IBackupRepository
from justai.interface_adapters.conversational_repository_interface import IConversationRepository
from typing import List
import copy


class AgentUseCases:
    def __init__(self,
                 agent_repository: IAgentRepository,
                 backup_repository: IBackupRepository,
                 conversation_repository: IConversationRepository):
        self.agent_repository = agent_repository
        self.backup_repository = backup_repository
        self.conversation_repository = conversation_repository

    def create(self, agent_name: str, agent_system_prompt: str) -> None:
        """
        Creates a new agent in the database.

        Args:
            agent_name (str): The name of the agent to delete.
            agent_system_prompt (str): The system prompt for the agent.

        Raises:
            DuplicateError: If an agent with the same name already exists.
        """
        existing_agent = self.agent_repository.get_by_name(agent_name)
        if existing_agent:
            raise DuplicateError(f"Agent with the name {agent_name} already exists.")
        agent = Agent(agent_name, agent_system_prompt)
        self.agent_repository.create(agent)

    def delete(self, agent_name: str) -> None:
        """
        Deletes an agent and backs up its linked conversations.

        Args:
            agent_name (str): The name of the agent to delete.
        """
        agent = self.agent_repository.get_by_name(agent_name)
        if not agent:
            raise NotFoundError(f"Agent with the name {agent_name} not found.")

        # Backup and delete linked conversations for the agent
        linked_conversations = self.conversation_repository.get_by_agent_name(agent.name)
        if linked_conversations:
            self.backup_repository.backup_conversations(linked_conversations)
            self.conversation_repository.delete_by_agent_name(agent.name)
        # Delete the agent
        self.agent_repository.delete(agent)

    def edit(self, agent_name: str, new_agent_name: str, new_system_prompt: str) -> None:
        """
        Edits agent details and updates associated conversations.

        Args:
            agent_name (str): The current name of the agent.
            new_agent_name (str): The new name for the agent.
            new_system_prompt (str): The new system prompt for the agent.
        """
        agent_to_edit = self.agent_repository.get_by_name(agent_name)
        if self.agent_repository.get_by_name(new_agent_name):
            raise DuplicateError(f"Agent with the name {new_agent_name} already exists.")
        if self.conversation_repository.get_by_agent_name(new_agent_name):
            raise DuplicateError(f"Conversations with the agent name {new_agent_name} already exists.")
        agent_new_version = Agent(new_agent_name, new_system_prompt)

        try:
            self.agent_repository.update(agent_to_edit, agent_new_version)
            self.conversation_repository.update_agent_field(agent_to_edit, agent_new_version)
        except Exception as e:
            # If there's an error, attempt a manual rollback.
            # This might involve deleting the agent if it was added,
            # and delete the associated conversations
            if (self.agent_repository.get_by_name(agent_new_version.name)):
                self.delete(agent_new_version.name)
            raise e

    def get_all(self) -> List[Agent]:
        """Returns a list of all agents."""
        return self.agent_repository.get_all()

    def get_one(self, agent_name: str) -> Agent:
        """Returns an agent object."""
        return self.agent_repository.get_by_name(agent_name)

    def recover(self, agent_name: str, agent_prompt: str) -> None:
        """
        Recovers an agent and its conversations from the backup.

        Args:
            agent_name (str): Name of the agent to recover.

        Raises:
            NotFoundError: If the agent's backup is not found.
            DataBaseError: For other generic database errors.
        """
        # Check if agent exists in the main repository (to prevent duplication)
        agent_in_main_repo = self.agent_repository.get_by_name(agent_name)
        if agent_in_main_repo:
            raise ValueError(f"Agent {agent_name} already exists in the main repository!")
        agent_to_recover = Agent(agent_name, agent_prompt)
        try:
            # Recover the agent first
            self.agent_repository.create(agent_to_recover)

            # Recover agent's conversations
            backed_up_conversations = self.backup_repository.get_conversations_by_agent_object(agent_to_recover)
            if not backed_up_conversations:
                raise NotFoundError(f"No backup found for agent: {agent_name}")

            self.conversation_repository.recover(backed_up_conversations)

        except Exception as e:
            # If there's an error, attempt a manual rollback.
            # This might involve deleting the agent if it was added,
            # or deleting the recovered conversations if they were added.
            if self.agent_repository.get_by_name(agent_to_recover.name):
                self.agent_repository.delete(agent_to_recover)
            if self.conversation_repository.get_by_agent_name(agent_to_recover.name):
                self.conversation_repository.delete_by_agent_object(agent_to_recover)
            raise e

        # If everything's successful till here, remove the backed up conversations
        self.backup_repository.delete_conversations_by_agent_object(agent_to_recover)

    def add_dataset_generation_prompt(self, agent_name: str, prompt_label: str, prompt: str) -> None:
        """
        Adds a dataset generation prompt to an agent.

        Args:
            agent_name (str): Name of the agent.
            prompt_label (str): Label for the dataset generation prompt.
            prompt (str): The dataset generation prompt to add.
        """
        current_agent = self.get_one(agent_name)
        if not current_agent:
            raise NotFoundError(f"Agent '{agent_name}' not found.")

        updated_agent = copy.deepcopy(current_agent)

        updated_agent.dataset_generation_prompts[prompt_label] = prompt

        # Update the agent in the repository using the provided update method
        self.agent_repository.update(current_agent, updated_agent)

    def delete_dataset_generation_prompt(self, agent_name: str, prompt_label: str) -> None:
        """
        Deletes a dataset generation prompt from an agent.

        Args:
            agent_name (str): Name of the agent.
            prompt_label (str): Label of the dataset generation prompt to delete.
        """
        current_agent = self.get_one(agent_name)
        if not current_agent:
            raise NotFoundError(f"Agent '{agent_name}' not found.")

        if prompt_label not in current_agent.dataset_generation_prompts:
            raise ValueError(f"Prompt labeled '{prompt_label}' not found in agent '{agent_name}'.")

        updated_agent = copy.deepcopy(current_agent)
        del updated_agent.dataset_generation_prompts[prompt_label]

        # Update the agent in the repository using the provided update method
        self.agent_repository.update(current_agent, updated_agent)
