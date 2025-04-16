class ServiceErrorHandler(Exception):
    """Exception raised form  server."""
    def __init__(self, message="An error occured please try again later."):
        self.message = message
        super().__init__(self.message)
