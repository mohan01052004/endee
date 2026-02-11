"""
Endee Python SDK - A Python client for the Endee vector database.
"""

from .client import EndeeClient
from .exceptions import EndeeError, EndeeConnectionError, EndeeAPIError

__version__ = "0.1.0"
__all__ = ["EndeeClient", "EndeeError", "EndeeConnectionError", "EndeeAPIError"]
