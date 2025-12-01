class AppBaseException(Exception):
    """Base class for all custom application exceptions."""
    pass

class DuplicateResourceError(AppBaseException):
    """Raised when an attempt is made to create a resource that already exists."""
    def __init__(self, message="Resource already exists"):
        self.message = message
        super().__init__(self.message)

class InternalDatabaseError(AppBaseException):
    """Raised for unexpected failures during database operations (e.g., connection lost)."""
    def __init__(self, message="Database operation failed"):
        self.message = message
        super().__init__(self.message)

class InsufficientPrivilegesError(AppBaseException):
    """Raised when a user attempts an action without the necessary role/permission."""
    def __init__(self, message="Insufficient privileges"):
        self.message = message
        super().__init__(self.message)