"""
Data models for Virasty API.
All models support dict-to-object conversion and proper typing.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """
    Represents a Virasty user profile.
    
    Examples:
        >>> user_data = {"userID": "123", "username": "john", "displayName": "John Doe"}
        >>> user = User.from_dict(user_data)
        >>> print(user)
        User(@john)
        >>> print(user.profile_url)
        https://virasty.com/@john
    """
    
    user_id: str = ""
    username: str = ""
    display_name: str = ""
    firstname: str = ""
    lastname: str = ""
    bio: str = ""
    avatar: str = ""
    profile_banner: str = ""
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    location: str = ""
    website: str = ""
    verified_type: str = ""
    gender: str = ""
    account_type: str = ""
    is_blocked: bool = False
    is_muted: bool = False
    is_following: bool = False
    is_follower: bool = False
    is_verified: bool = False
    join_date: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """
        Create a User instance from API response dictionary.
        
        Args:
            data: Raw dictionary from API response
            
        Returns:
            User: Parsed user object
            
        Example:
            >>> data = {"userID": "123", "username": "alice"}
            >>> user = User.from_dict(data)
        """
        if not data:
            return cls()
            
        bio_data = data.get("bio", {})
        bio_text = bio_data.get("text", "") if isinstance(bio_data, dict) else str(bio_data)
        
        verified = data.get("verifiedType", "")
        
        return cls(
            user_id=str(data.get("userID", "")),
            username=data.get("username", ""),
            display_name=data.get("displayName", ""),
            firstname=data.get("firstname", ""),
            lastname=data.get("lastname", ""),
            bio=bio_text,
            avatar=data.get("avatar", ""),
            profile_banner=data.get("profileBanner", ""),
            followers_count=data.get("followersCount", 0),
            following_count=data.get("followingsCount", 0),
            posts_count=data.get("postsCount", 0),
            location=data.get("location", ""),
            website=data.get("website", ""),
            verified_type=verified,
            gender=data.get("gender", ""),
            account_type=data.get("type", ""),
            is_blocked=data.get("isBlocked", False),
            is_muted=data.get("isMute", False),
            is_following=data.get("isFollowing", False),
            is_follower=data.get("isFollower", False),
            is_verified=bool(verified and verified != "none"),
            join_date=data.get("createdTime"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user back to dictionary format."""
        return {
            "userID": self.user_id,
            "username": self.username,
            "displayName": self.display_name,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "bio": self.bio,
            "avatar": self.avatar,
            "profileBanner": self.profile_banner,
            "followersCount": self.followers_count,
            "followingsCount": self.following_count,
            "postsCount": self.posts_count,
            "location": self.location,
            "website": self.website,
            "verifiedType": self.verified_type,
            "gender": self.gender,
            "type": self.account_type,
            "isBlocked": self.is_blocked,
            "isMute": self.is_muted,
            "isFollowing": self.is_following,
            "isFollower": self.is_follower,
        }
    
    @property
    def profile_url(self) -> str:
        """Full URL to user's profile."""
        return f"https://virasty.com/@{self.username}" if self.username else ""
    
    @property
    def mention(self) -> str:
        """Mention format: @username"""
        return f"@{self.username}" if self.username else ""
    
    @property
    def full_name(self) -> str:
        """Full name (firstname + lastname) or display name."""
        if self.firstname or self.lastname:
            return f"{self.firstname} {self.lastname}".strip()
        return self.display_name or self.username
    
    @property
    def avatar_url(self) -> Optional[str]:
        """Full avatar URL if exists."""
        if not self.avatar:
            return None
        if self.avatar.startswith('http'):
            return self.avatar
        return f"https://virasty.com/{self.avatar.lstrip('/')}"
    
    def __str__(self) -> str:
        if self.display_name and self.username:
            return f"{self.display_name} (@{self.username})"
        return f"@{self.username}" if self.username else "Unknown User"
    
    def __repr__(self) -> str:
        return f"User(id={self.user_id}, username='{self.username}')"


@dataclass
class Post:
    """
    Represents a Virasty post/thread/reply.
    
    Examples:
        >>> post_data = {"ID": "456", "text": "Hello World"}
        >>> post = Post.from_dict(post_data)
        >>> print(post.text)
        Hello World
        >>> print(post.url)
        https://virasty.com/@user/post/456
    """
    
    post_id: str = ""
    user_id: str = ""
    text: str = ""
    post_type: str = "post"  # post, reply, thread, repost
    media_type: str = "none"  # none, image, video, audio, file
    replies_count: int = 0
    reposts_count: int = 0
    repost_quotes_count: int = 0
    reactions_count: int = 0
    view_count: int = 0
    bookmark_count: int = 0
    created_time: int = 0
    edited_time: int = 0
    user_reaction: str = ""  # like, love, haha, etc.
    reposted_by_me: bool = False
    is_bookmarked: bool = False
    is_deleted: bool = False
    is_pinned: bool = False
    is_sensitive: bool = False
    language: str = "fa"
    reply_policy: str = "all"  # all, following, mentioned
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    media: List[Dict[str, Any]] = field(default_factory=list)
    poll: Optional[Dict[str, Any]] = None
    user: Optional[User] = None
    reposted_post: Optional["Post"] = None
    reply_to_post_id: Optional[str] = None
    thread_root_post_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Post":
        """
        Create a Post instance from API response dictionary.
        
        Args:
            data: Raw dictionary from API response
            
        Returns:
            Post: Parsed post object
        """
        if not data:
            return cls()
        
        # Extract reactions data
        reactions_data = data.get("postReactions", {}) or {}
        
        # Extract user data
        user_data = data.get("userSummary") or data.get("user")
        user = User.from_dict(user_data) if user_data else None
        
        # Extract reposted post
        repost_data = data.get("repostedPostSummary")
        reposted_post = Post.from_dict(repost_data) if repost_data else None
        
        # Extract extra data
        extra = data.get("extraData", {}) or {}
        
        # Extract media
        media = extra.get("media", data.get("media", []))
        if not isinstance(media, list):
            media = []
        
        # Extract hashtags and mentions from text
        hashtags = cls._extract_hashtags(data.get("text", ""))
        mentions = cls._extract_mentions(data.get("text", ""))
        
        # Extract poll
        poll = data.get("poll")
        
        return cls(
            post_id=str(data.get("ID", "")),
            user_id=str(data.get("userID", "")),
            text=data.get("text", ""),
            post_type=data.get("repostType") or data.get("type", "post"),
            media_type=data.get("mediaType", "none"),
            replies_count=data.get("repliesCount", 0),
            reposts_count=data.get("repostsCount", 0),
            repost_quotes_count=data.get("repostQuotesCount", 0),
            reactions_count=reactions_data.get("reactionsCount", 0),
            view_count=data.get("viewCount", 0),
            bookmark_count=data.get("bookmarkCount", 0),
            created_time=data.get("createdTime", 0),
            edited_time=data.get("editedTime", 0),
            user_reaction=reactions_data.get("userReaction", ""),
            reposted_by_me=data.get("repostedByMe", False),
            is_bookmarked=data.get("isBookmarked", False),
            is_deleted=data.get("isDeleted", False),
            is_pinned=data.get("isPinned", False),
            is_sensitive=data.get("isSensitive", False),
            language=data.get("language", "fa"),
            reply_policy=data.get("replyPolicy", "all"),
            hashtags=hashtags,
            mentions=mentions,
            media=media,
            poll=poll,
            user=user,
            reposted_post=reposted_post,
            reply_to_post_id=data.get("replyPostID"),
            thread_root_post_id=data.get("threadRootPostID"),
        )
    
    @staticmethod
    def _extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from post text."""
        import re
        return re.findall(r'#(\w+)', text)
    
    @staticmethod
    def _extract_mentions(text: str) -> List[str]:
        """Extract mentions from post text."""
        import re
        return re.findall(r'@(\w+)', text)
    
    @property
    def url(self) -> str:
        """Full URL to the post."""
        if self.user and self.user.username:
            return f"https://virasty.com/@{self.user.username}/post/{self.post_id}"
        return f"https://virasty.com/post/{self.post_id}"
    
    @property
    def created_datetime(self) -> Optional[datetime]:
        """Creation time as datetime object."""
        if self.created_time:
            return datetime.fromtimestamp(self.created_time / 1000)
        return None
    
    @property
    def edited_datetime(self) -> Optional[datetime]:
        """Last edit time as datetime object."""
        if self.edited_time:
            return datetime.fromtimestamp(self.edited_time / 1000)
        return None
    
    @property
    def is_reply(self) -> bool:
        """Check if post is a reply."""
        return self.post_type == "reply"
    
    @property
    def is_repost(self) -> bool:
        """Check if post is a repost."""
        return self.post_type == "repost"
    
    @property
    def is_thread(self) -> bool:
        """Check if post is a thread."""
        return self.post_type == "thread"
    
    @property
    def has_media(self) -> bool:
        """Check if post has media attachments."""
        return self.media_type != "none" and len(self.media) > 0
    
    @property
    def has_poll(self) -> bool:
        """Check if post has a poll."""
        return self.poll is not None and len(self.poll) > 0
    
    @property
    def summary(self) -> str:
        """Short text preview."""
        max_length = 100
        text = self.text.replace('\n', ' ').strip()
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert post to dictionary."""
        return {
            "ID": self.post_id,
            "userID": self.user_id,
            "text": self.text,
            "type": self.post_type,
            "mediaType": self.media_type,
            "repliesCount": self.replies_count,
            "repostsCount": self.reposts_count,
            "viewCount": self.view_count,
            "createdTime": self.created_time,
            "language": self.language,
        }
    
    def __str__(self) -> str:
        return f"Post: {self.summary}"
    
    def __repr__(self) -> str:
        return f"Post(id={self.post_id}, type='{self.post_type}', user_id={self.user_id})"


@dataclass
class Notification:
    """
    Represents a Virasty notification.
    
    Examples:
        >>> notif_data = {"ID": "789", "type": "follow"}
        >>> notif = Notification.from_dict(notif_data)
        >>> print(notif.notification_type)
        follow
    """
    
    notification_id: str = ""
    notification_type: str = ""  # follow, like, reply, repost, mention, etc.
    created_time: int = 0
    is_read: bool = False
    is_seen: bool = False
    actor: Optional[User] = None
    post: Optional[Post] = None
    message: str = ""
    action_url: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """
        Create a Notification instance from API response.
        
        Args:
            data: Raw dictionary from API response
            
        Returns:
            Notification: Parsed notification object
        """
        if not data:
            return cls()
        
        # Extract actor user
        actor_data = data.get("actorSummary") or data.get("userSummary")
        actor = User.from_dict(actor_data) if actor_data else None
        
        # Extract related post
        post_data = data.get("postInfo") or data.get("post")
        post = Post.from_dict(post_data) if post_data else None
        
        return cls(
            notification_id=str(data.get("ID", "")),
            notification_type=data.get("type", ""),
            created_time=data.get("createdTime", 0),
            is_read=data.get("isRead", False),
            is_seen=data.get("isSeen", False),
            actor=actor,
            post=post,
            message=data.get("message", ""),
            action_url=data.get("actionURL", ""),
        )
    
    @property
    def created_datetime(self) -> Optional[datetime]:
        """Creation time as datetime object."""
        if self.created_time:
            return datetime.fromtimestamp(self.created_time / 1000)
        return None
    
    @property
    def type_emoji(self) -> str:
        """Get emoji for notification type."""
        emoji_map = {
            "follow": "👤",
            "like": "❤️",
            "reply": "💬",
            "repost": "🔄",
            "mention": "📢",
            "message": "✉️",
            "poll": "📊",
            "campaign": "🎯",
        }
        return emoji_map.get(self.notification_type, "🔔")
    
    @property
    def description(self) -> str:
        """Human-readable notification description."""
        if not self.actor:
            return "Unknown notification"
        
        actor_name = str(self.actor)
        
        descriptions = {
            "follow": f"{actor_name} followed you",
            "like": f"{actor_name} liked your post",
            "reply": f"{actor_name} replied to your post",
            "repost": f"{actor_name} reposted your post",
            "mention": f"{actor_name} mentioned you",
            "message": f"{actor_name} sent you a message",
        }
        
        return descriptions.get(self.notification_type, f"{actor_name}: {self.notification_type}")
    
    def __str__(self) -> str:
        return f"{self.type_emoji} {self.description}"
    
    def __repr__(self) -> str:
        return f"Notification(id={self.notification_id}, type='{self.notification_type}')"


@dataclass
class Conversation:
    """
    Represents a direct message conversation.
    """
    
    conversation_id: str = ""
    user: Optional[User] = None
    last_message: str = ""
    last_message_time: int = 0
    unread_count: int = 0
    is_confirmed: bool = False
    is_blocked: bool = False
    is_muted: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create Conversation from API response."""
        if not data:
            return cls()
        
        user_data = data.get("userSummary") or data.get("user")
        user = User.from_dict(user_data) if user_data else None
        
        last_msg = data.get("lastMessage", {}) or {}
        
        return cls(
            conversation_id=str(data.get("ID", "")),
            user=user,
            last_message=last_msg.get("text", ""),
            last_message_time=last_msg.get("createdTime", 0),
            unread_count=data.get("unseenCount", 0),
            is_confirmed=data.get("isConfirmed", False),
            is_blocked=data.get("isBlocked", False),
            is_muted=data.get("isMute", False),
        )
    
    @property
    def last_message_datetime(self) -> Optional[datetime]:
        """Last message time as datetime."""
        if self.last_message_time:
            return datetime.fromtimestamp(self.last_message_time / 1000)
        return None
    
    def __str__(self) -> str:
        user_str = str(self.user) if self.user else "Unknown"
        return f"Conversation with {user_str}"
    
    def __repr__(self) -> str:
        return f"Conversation(id={self.conversation_id})"


@dataclass
class Message:
    """
    Represents a direct message.
    """
    
    message_id: str = ""
    sender_id: str = ""
    receiver_id: str = ""
    text: str = ""
    created_time: int = 0
    is_read: bool = False
    is_mine: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create Message from API response."""
        if not data:
            return cls()
        
        return cls(
            message_id=str(data.get("ID", "")),
            sender_id=str(data.get("senderUserID", "")),
            receiver_id=str(data.get("receiverUserID", "")),
            text=data.get("text", ""),
            created_time=data.get("createdTime", 0),
            is_read=data.get("isRead", False),
            is_mine=data.get("isMine", False),
        )
    
    @property
    def created_datetime(self) -> Optional[datetime]:
        """Creation time as datetime."""
        if self.created_time:
            return datetime.fromtimestamp(self.created_time / 1000)
        return None
    
    def __str__(self) -> str:
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Message: {preview}"
    
    def __repr__(self) -> str:
        return f"Message(id={self.message_id})"


@dataclass
class Poll:
    """
    Represents a poll in a post.
    """
    
    poll_id: str = ""
    question: str = ""
    options: List[Dict[str, Any]] = field(default_factory=list)
    total_votes: int = 0
    expire_time: int = 0
    has_voted: bool = False
    voted_option_id: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Poll":
        """Create Poll from API response."""
        if not data:
            return cls()
        
        return cls(
            poll_id=str(data.get("ID", "")),
            question=data.get("question", ""),
            options=data.get("pollOptions", []),
            total_votes=data.get("totalVotes", 0),
            expire_time=data.get("expireTime", 0),
            has_voted=data.get("hasVoted", False),
            voted_option_id=data.get("votedOptionID", ""),
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if poll has expired."""
        if self.expire_time:
            return datetime.now().timestamp() > (self.expire_time / 1000)
        return False
    
    @property
    def results(self) -> List[Dict[str, Any]]:
        """Get poll results with percentages."""
        if not self.total_votes:
            return []
        
        results = []
        for option in self.options:
            vote_count = option.get("voteCount", 0)
            percentage = (vote_count / self.total_votes * 100) if self.total_votes > 0 else 0
            results.append({
                "title": option.get("title", ""),
                "votes": vote_count,
                "percentage": round(percentage, 1),
                "is_voted": option.get("ID") == self.voted_option_id,
            })
        return results
    
    def __str__(self) -> str:
        return f"Poll: {self.question}"
    
    def __repr__(self) -> str:
        return f"Poll(id={self.poll_id}, votes={self.total_votes})"


@dataclass
class Campaign:
    """
    Represents a campaign post.
    """
    
    campaign_id: str = ""
    title: str = ""
    description: str = ""
    campaign_type: str = ""
    status: str = ""
    supporter_count: int = 0
    hashtags: List[str] = field(default_factory=list)
    creator: Optional[User] = None
    created_time: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Campaign":
        """Create Campaign from API response."""
        if not data:
            return cls()
        
        user_data = data.get("userSummary")
        creator = User.from_dict(user_data) if user_data else None
        
        return cls(
            campaign_id=str(data.get("ID", "")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            campaign_type=data.get("type", ""),
            status=data.get("status", ""),
            supporter_count=data.get("supporterCount", 0),
            hashtags=data.get("hashtags", []),
            creator=creator,
            created_time=data.get("createdTime", 0),
        )
    
    def __str__(self) -> str:
        return f"Campaign: {self.title}"
    
    def __repr__(self) -> str:
        return f"Campaign(id={self.campaign_id}, type='{self.campaign_type}')"


@dataclass
class CloudMeeting:
    """
    Represents a cloud meeting/voice room.
    """
    
    meeting_id: str = ""
    room_name: str = ""
    status: str = ""  # created, started, ended
    participants_count: int = 0
    speakers_count: int = 0
    created_time: int = 0
    creator: Optional[User] = None
    is_incognito_allowed: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CloudMeeting":
        """Create CloudMeeting from API response."""
        if not data:
            return cls()
        
        user_data = data.get("userSummary") or data.get("creator")
        creator = User.from_dict(user_data) if user_data else None
        
        return cls(
            meeting_id=str(data.get("ID", "")),
            room_name=data.get("roomName", ""),
            status=data.get("status", ""),
            participants_count=data.get("participantsCount", 0),
            speakers_count=data.get("speakersCount", 0),
            created_time=data.get("createdTime", 0),
            creator=creator,
            is_incognito_allowed=data.get("isIncognitoAllowed") == "allowed",
        )
    
    @property
    def is_active(self) -> bool:
        """Check if meeting is currently active."""
        return self.status in ["started", "created"]
    
    def __str__(self) -> str:
        return f"Meeting: {self.room_name} ({self.participants_count} participants)"
    
    def __repr__(self) -> str:
        return f"CloudMeeting(id={self.meeting_id}, status='{self.status}')"


# Export all models
__all__ = [
    "User",
    "Post",
    "Notification",
    "Conversation",
    "Message",
    "Poll",
    "Campaign",
    "CloudMeeting",
]