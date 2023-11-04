from typing import Dict


class User:
    """
    Represents a user with a user_name.

    Attributes:
    - user_name (str): The unique name or identifier of the user.

    Methods:
    - to_dict: Returns a dictionary representation of the User.
    """
    def __init__(self, user_name: str):
        self.user_name = user_name

    def to_dict(self) -> Dict[str, str]:
        return {
            'user_name': self.user_name
        }

    def __repr__(self) -> str:
        return f"User(user_name={self.user_name})"
