class DuplicateError(Exception):
    """Raised when a duplicate record is found."""
    def __init__(self, message="A record with the same identifier already exists."):
        self.message = message
        super().__init__(self.message)


class DataBaseError(Exception):
    """Raised for generic database errors."""
    def __init__(self, message="An error occurred with the database operation."):
        self.message = message
        super().__init__(self.message)


class AgentNotFoundError(Exception):
    """Raised when an agent is not found."""
    def __init__(self, message="The specified agent could not be found."):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """Raised when an object is not found."""
    def __init__(self, message="The requested object could not be found."):
        self.message = message
        super().__init__(self.message)
