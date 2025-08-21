class APIException(Exception):
    """
    Custom exception class for API errors.
    """
    def __init__(self, status_code: int, success: bool, message: str, data=None, errors=None):
        """
        Initializes the APIException with a message.
        :param message:
        """
        super().__init__(message)
        self.status_code: int = status_code
        self.success: bool = success
        self.message: str = message
        self.data = data
        self.errors = errors
