"""
aiovir - Async Python client for Virasty messenger.
"""

from .client import VirastyClient
from .auth import VirastyAuth
from .decode import VirastyDecoder
from .models import (
    User,
    Post,
    Notification,
    Conversation,
    Message,
    Poll,
    Campaign,
    CloudMeeting,
)

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    "VirastyClient",
    "VirastyAuth",
    "VirastyDecoder",
    "User",
    "Post",
    "Notification",
    "Conversation",
    "Message",
    "Poll",
    "Campaign",
    "CloudMeeting",
]