"""
Custom exceptions for the complaints app.
Follows the principle of explicit error handling and clean code.
"""


class ComplaintServiceError(Exception):
    """Base exception for complaint service errors."""
    pass


class ComplaintNotFoundError(ComplaintServiceError):
    """Raised when a complaint is not found."""
    pass


class AgentNotFoundError(ComplaintServiceError):
    """Raised when an agent is not found or invalid."""
    pass


class InvalidStatusError(ComplaintServiceError):
    """Raised when an invalid status is provided."""
    pass


class PermissionDeniedError(ComplaintServiceError):
    """Raised when user doesn't have permission to perform an action."""
    pass


class ValidationError(ComplaintServiceError):
    """Raised when data validation fails."""
    pass