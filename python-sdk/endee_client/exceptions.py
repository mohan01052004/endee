"""
Custom exceptions for the Endee Python SDK.
"""


class EndeeError(Exception):
    """Base exception for all Endee SDK errors."""
    pass


class EndeeConnectionError(EndeeError):
    """Raised when connection to Endee server fails."""
    pass


class EndeeAPIError(EndeeError):
    """Raised when Endee API returns an error response."""
    
    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
