from typing import List
from justai.application.exceptions import DuplicateError, NotFoundError
from justai.entities.user import User
from justai.interface_adapters.conversational_repository_interface import IUserRepository


class UserUseCases:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def create(self, user_name: str) -> None:
        """
        Creates a new user in the database.

        Args:
            user_name (str): The name of the user to create.

        Raises:
            DuplicateError: If a user with the same name already exists.
        """
        existing_user = self.user_repository.get_by_name(user_name)
        if existing_user:
            raise DuplicateError(f"User with the name {user_name} already exists.")
        user = User(user_name)
        self.user_repository.create(user)

    def get_all(self) -> List[User]:
        """Returns a list of all users."""
        return self.user_repository.get_all()

    def get(self, user_name: str) -> User:
        """Returns a user object."""
        return self.user_repository.get_by_name(user_name)

    def delete(self, user_name: str) -> None:
        """
        Deletes a user from the database.

        Args:
            user_name (str): The name of the user to delete.

        Raises:
            NotFoundError: If the user with the given name is not found.
        """
        user = self.user_repository.get_by_name(user_name)
        if not user:
            raise NotFoundError(f"User with the name {user_name} not found.")
        self.user_repository.delete(user)

    def edit(self, current_user_name: str, new_user_name: str) -> None:
        """
        Edits the name of an existing user.

        Args:
            current_user_name (str): The current name of the user.
            new_user_name (str): The new name for the user.

        Raises:
            DuplicateError: If a user with the new name already exists.
            NotFoundError: If the user with the current name is not found.
        """
        # Check if a user with the new name already exists
        if self.user_repository.get_by_name(new_user_name):
            raise DuplicateError(f"User with the name {new_user_name} already exists.")

        # Fetch the user to edit using the current name
        user_to_edit = self.user_repository.get_by_name(current_user_name)
        if not user_to_edit:
            raise NotFoundError(f"User with the name {current_user_name} not found.")

        # Update the user's name
        new_user = User(new_user_name)
        self.user_repository.update(user_to_edit, new_user)
