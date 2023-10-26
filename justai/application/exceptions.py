class DuplicateError(Exception):
    """Raised when a duplicate record is found."""
    pass


class DataBaseError(Exception):
    """Raised for generic database errors."""
    pass


class AgentNotFoundError(Exception):
    """Raised when an agent is not found."""
    pass


class NotFoundError(Exception):
    """Raised when an object is not found."""
    pass
