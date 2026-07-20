"""
Async HTTP client for Virasty API.
"""

import asyncio
from pathlib import Path
import aiohttp
from .decode import VirastyDecoder
from .auth import VirastyAuth
from .models import User
from aiohttp_socks import ProxyConnector
from typing import Optional, Dict, Any, List

class VirastyClient:
    """
    Main async client for Virasty API.
    
    Usage:
        async with VirastyClient(session_file="session.vir") as client:
            await client.login("mobile", "password")
            me = await client.get_me()
            print(f"@{me.username}")
    """

    BASE_URL = "https://api.virasty.com"
    VIRASTY_URL = "https://virasty.com"

    def __init__(
        self,
        token: Optional[str] = None,
        session_file: Optional[str] = None,
        duid: Optional[str] = None,
        proxy: Optional[str] = None
    ):
        self.auth = VirastyAuth(session_file)
        self.decoder = VirastyDecoder(duid)
        self.proxy = proxy
        self._session: Optional[aiohttp.ClientSession] = None

        if token:
            self.auth.token = token

    async def __aenter__(self):
        connector = None
        if self.proxy:
            from aiohttp_socks import ProxyConnector
            connector = ProxyConnector.from_url(self.proxy)

        self._session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()
            self._session = None

    @property
    def http(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError("Use 'async with VirastyClient() as client:' block.")
        return self._session

    def _headers(self, extra: Dict = None) -> Dict[str, str]:
        h = {
            "accept": "*/*",
            "accept-language": "fa",
            "api-version": "1",
            "app-version": "1",
            "content-type": "application/octet-stream",
            "duid": self.decoder.duid or "",
            "origin": "https://virasty.com",
            "os": "windows",
            "platform": "web",
            "referer": "https://virasty.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        if self.auth.token:
            h["token"] = self.auth.token
        if extra:
            h.update(extra)
        return h

    async def _get(self, path: str, base_url: str = None) -> Any:
        url = f"{base_url or self.VIRASTY_URL}{path}"
        h = self._headers()
        h["content-type"] = "application/json"

        async with self.http.get(url, headers=h) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _post(self, path: str, data: Dict = None,
                    extra_headers: Dict = None, retry: int = 3) -> Any:
        url = f"{self.BASE_URL}{path}"
        h = self._headers(extra_headers)
        body = self.decoder.encrypt_request(path, data or {})

        for attempt in range(retry):
            async with self.http.post(url, data=body, headers=h) as resp:
                if resp.status == 429 and attempt < retry - 1:
                    wait = max(int(resp.headers.get("X-Ratelimit-Reset", 10)), 5)
                    await asyncio.sleep(wait)
                    continue

                resp.raise_for_status()
                return self.decoder.decrypt_response(await resp.read())


    async def login(self, username: str, password: str) -> bool:
        """Login with mobile and password. Session auto-saved to session file on success."""
        otp = await self._post(
            "/otp/sendByMobile",
            {"countryCode": "+98", "mobile": username}
        )

        if otp.get("status") != "success":
            return False

        result = await self._post(
            "/user/login",
            {
                "password": password,
                "deviceInfo": {
                    "OS": "windows",
                    "manufacturer": "Windows",
                    "model": "Microsoft Edge",
                    "OSVersion": "150"
                }
            },
            extra_headers={"verified-token": otp["data"]["verifiedToken"]}
        )

        if result.get("status") != "success":
            return False

        self.auth.save(
            token=result["data"]["token"],
            s_token=result["data"].get("sToken", ""),
            username=username
        )

        return True

    def logout(self) -> None:
        self.auth.clear()


    async def get_me(self) -> User:
        data = await self._post("/user/info/me")
        return User.from_dict(data["data"]["user"])


    async def get_notification_badge(self) -> Dict:
        return await self._post("/notification/badge")

    async def get_notifications(self, page_size: int = 50, action: str = "down", notification_id: str = "0", seen: bool = None) -> Dict:
        payload = {"pageSize": page_size, "action": action, "notificationID": notification_id}
        if seen is not None:
            payload["seen"] = seen
        return await self._post("/notification/list", payload)

    async def mark_all_notifications_read(self) -> bool:
        await self._post("/notification/seen")
        return True

    async def clear_all_notifications(self) -> bool:
        await self._post("/notification/clear", {"type": ""})
        return True

    async def get_trends(self) -> Dict:
        return await self._post("/trend/list")

    async def get_version(self) -> Dict:
        return await self._get("/version.json")

    async def get_server_time(self) -> Dict:
        return await self._post("/time/now")

    async def get_post(self, post_id: str) -> Dict:
        return await self._post("/post/get", {"postID": post_id})

    async def create_post(
        self,
        text: str,
        media: list = None,
        reply_post_id: str = None,
        root_post_id: str = None,
        thread_root_post_id: str = None,
        reply_policy: str = "all",
        community_id: str = None,
        poll_id: str = None,
        campaign_id: str = None,
        cloud_meeting_id: str = None,
        live_stream_id: str = None,
        title: str = None,
        extra_data: Dict = None,
        **kwargs
    ) -> Dict:
        payload = {"text": text}
        if media:
            payload["media"] = media
        if reply_post_id:
            payload["replyPostID"] = reply_post_id
        if root_post_id:
            payload["rootPostID"] = root_post_id
        if thread_root_post_id:
            payload["threadRootPostID"] = thread_root_post_id
        if reply_policy:
            payload["replyPolicy"] = reply_policy
        if community_id:
            payload["communityID"] = community_id
        if poll_id:
            payload["pollID"] = poll_id
        if campaign_id:
            payload["campaignID"] = campaign_id
        if cloud_meeting_id:
            payload["cloudMeetingID"] = cloud_meeting_id
        if live_stream_id:
            payload["liveStreamID"] = live_stream_id
        if title:
            payload["extraData"] = payload.get("extraData", {})
            payload["extraData"]["title"] = title
        if extra_data:
            payload["extraData"] = payload.get("extraData", {})
            payload["extraData"].update(extra_data)
        payload.update(kwargs)
        return await self._post("/post/create", payload)

    async def edit_post(self, post_id: str, text: str, title: str = None, styles: list = None) -> Dict:
        payload = {"postID": post_id, "text": text}
        if title is not None:
            payload["title"] = title
        if styles:
            payload["styles"] = styles
        return await self._post("/post/edit", payload)

    async def delete_post(self, post_id: str) -> Dict:
        return await self._post("/post/remove", {"postID": post_id})

    async def toggle_reaction(self, post_id: str, reaction: str) -> Dict:
        return await self._post("/post/reaction/set", {"postID": post_id, "reaction": reaction})

    async def repost(self, post_id: str) -> Dict:
        return await self._post("/post/repost", {"postID": post_id})

    async def undo_repost(self, post_id: str) -> Dict:
        return await self._post("/post/repost/undo", {"postID": post_id})

    async def bookmark(self, post_id: str, add: bool = True) -> Dict:
        return await self._post("/bookmark/set", {"postID": post_id, "operation": "set" if add else "unset"})

    async def get_replies(self, post_id: str, action: str = "down", last_post_id: str = "0", order: str = "asc") -> Dict:
        return await self._post("/post/replies/list", {
            "postID": post_id,
            "action": action,
            "postID": last_post_id,
            "order": order
        })

    async def get_reposts(self, post_id: str, page: int = 1) -> Dict:
        return await self._post("/post/reposts/list", {"postID": post_id, "pageNumber": page})

    async def get_repost_quotes(self, post_id: str, page: int = 1) -> Dict:
        return await self._post("/post/repostQuotes/list", {"postID": post_id, "pageNumber": page})

    async def get_reactioners(self, post_id: str, page: int = 1) -> Dict:
        return await self._post("/post/reactionersList", {"postID": post_id, "pageNumber": page})

    async def pin_post(self, post_id: str, pin: bool = True) -> Dict:
        return await self._post("/post/pin", {"postID": post_id, "operation": "pin" if pin else "unpin"})

    async def report_post(self, post_id: str, abuse_category_id: str, description: str) -> Dict:
        return await self._post("/post/abuseReport", {
            "postID": post_id,
            "abuseCategoryID": abuse_category_id,
            "description": description
        })

    async def get_user_posts(self, user_id: str, post_id: str = "0", action: str = "down", type: str = "posts") -> Dict:
        return await self._post("/post/list", {
            "userID": user_id,
            "postID": post_id,
            "action": action,
            "type": type
        })

    async def get_feed(self, action: str = "", post_id: str = "0", type: str = None, attachment_type: str = None, topic_id: str = None) -> Dict:
        payload = {"action": action, "postID": post_id}
        if type:
            payload["type"] = type
        if attachment_type:
            payload["attachmentType"] = attachment_type
        if topic_id:
            payload["topicID"] = topic_id
        return await self._post("/post/feed", payload)

    async def get_feed_for_you(self, pagination: str = None) -> Dict:
        return await self._post("/post/feed/forYou", {"pagination": pagination} if pagination else {})

    async def get_post_stats(self, post_id: str) -> Dict:
        return await self._post("/post/stat", {"postID": post_id})

    async def get_bookmarks(self, action: str = "down", bookmark_id: str = "0") -> Dict:
        return await self._post("/bookmark/list", {"action": action, "bookmarkID": bookmark_id})

    async def clear_bookmarks(self) -> Dict:
        return await self._post("/bookmark/clearAll")

    async def get_feed_update(self, type: str = None, attachment_type: str = None, topic_id: str = None) -> Dict:
        payload = {}
        if type:
            payload["type"] = type
        if attachment_type:
            payload["attachmentType"] = attachment_type
        if topic_id:
            payload["topicID"] = topic_id
        return await self._post("/post/feed/getUpdate", payload)

    async def update_post_rating(self, post_id: str, score: int, direction: str = "increase") -> Dict:
        return await self._post("/post/ratingScore/update", {
            "postID": post_id,
            "ratingScore": score,
            "type": direction
        })

    async def mute_post_mentions(self, post_id: str, mute: bool = True) -> Dict:
        return await self._post("/post/mentions/mute", {
            "postID": post_id,
            "operation": "mute" if mute else "unmute"
        })

    async def get_edit_history(self, post_id: str) -> Dict:
        return await self._post("/post/edit/history", {"postID": post_id})

    async def set_post_title(self, post_id: str, title: str) -> Dict:
        return await self._post("/post/title/set", {"postID": post_id, "title": title})

    async def remove_post_title(self, post_id: str) -> Dict:
        return await self._post("/post/title/remove", {"postID": post_id})

    async def add_media_to_post(self, post_id: str, media_sid: str, caption: str = "", cover_sid: str = "", url: str = "") -> Dict:
        return await self._post("/post/media/add", {
            "postID": post_id,
            "media": [{"SID": media_sid, "caption": caption, "coverSID": cover_sid, "url": url}]
        })

    async def remove_media_from_post(self, post_id: str, media_sid: str, dont_remove_post: bool = False) -> Dict:
        return await self._post("/post/media/remove", {
            "postID": post_id,
            "SID": media_sid,
            "dontRemovePost": dont_remove_post
        })

    async def update_media_caption(self, post_media_id: str, caption: str, url: str = "", cover_sid: str = "") -> Dict:
        return await self._post("/post/media/update", {
            "postMediaID": post_media_id,
            "caption": caption,
            "url": url,
            "coverSID": cover_sid
        })

    async def fact_check_post(self, post_id: str, fact_type: str) -> Dict:
        # fact_type: "fake", "fact", "semiAccurate", "misleading", etc.
        return await self._post("/post/factChecking", {"postID": post_id, "type": fact_type})

    async def get_public_feed(self) -> Dict:
        return await self._post("/post/feed/public")


    async def create_poll(self, question: str, options: list, expire_time: int, who_can_see: str = "noOne") -> Dict:
        return await self._post("/poll/create", {
            "question": question,
            "pollOptions": [{"title": opt} for opt in options],
            "expireTime": expire_time,
            "whoCanSeeParticipants": who_can_see
        })

    async def vote_poll(self, poll_id: str, option_id: str) -> Dict:
        return await self._post("/poll/vote", {"pollID": poll_id, "optionID": option_id})

    async def retract_vote(self, poll_id: str) -> Dict:
        return await self._post("/poll/retract", {"pollID": poll_id})

    async def get_poll_participants(self, poll_id: str, action: str = "down", page_id: str = "0") -> Dict:
        return await self._post("/poll/participants/list", {
            "pollID": poll_id,
            "action": action,
            "pageID": page_id
        })

    async def create_campaign(self, title: str, description: str, type: str, hashtags: list = None,
                              responsible_persons: list = None, urls: list = None) -> Dict:
        payload = {
            "title": title,
            "description": description,
            "type": type,
        }
        if hashtags:
            payload["hashtags"] = hashtags
        if responsible_persons:
            payload["responsiblePersons"] = responsible_persons
        if urls:
            payload["urls"] = urls
        return await self._post("/campaign/create", payload)

    async def support_campaign(self, campaign_id: str) -> Dict:
        return await self._post("/campaign/support", {"campaignID": campaign_id})

    async def update_campaign_status(self, campaign_id: str, status: str, description: str = "", importance_factor: str = "1") -> Dict:
        return await self._post("/campaign/status/update", {
            "campaignID": campaign_id,
            "status": status,
            "description": description,
            "importanceFactor": importance_factor
        })

    async def update_campaign(self, campaign_id: str, title: str = None, description: str = None,
                              type: str = None, responsible_persons: list = None) -> Dict:
        payload = {"campaignID": campaign_id}
        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if type:
            payload["type"] = type
        if responsible_persons is not None:
            payload["responsiblePersons"] = responsible_persons
        return await self._post("/campaign/update", payload)

    async def get_campaign_followups(self, campaign_followup_user_id: str = "0", action: str = "down") -> Dict:
        return await self._post("/campaign/followupUser/inProgress", {
            "postCampaignFollowupUserID": campaign_followup_user_id,
            "action": action
        })

    async def add_campaign_followup(self, campaign_id: str, user_id: str) -> Dict:
        return await self._post("/campaign/followupUser/set", {
            "postCampaignID": campaign_id,
            "followupUserID": user_id
        })

    async def remove_campaign_followup(self, campaign_id: str, user_id: str) -> Dict:
        return await self._post("/campaign/followupUser/remove", {
            "postCampaignID": campaign_id,
            "followupUserID": user_id
        })

    async def add_followup_result(self, campaign_id: str, post_id: str) -> Dict:
        return await self._post("/campaign/followup/addResult", {
            "campaignPostID": campaign_id,
            "followupPostID": post_id
        })

    async def remove_followup_result(self, campaign_id: str, post_id: str) -> Dict:
        return await self._post("/campaign/followup/removeResult", {
            "campaignPostID": campaign_id,
            "followupPostID": post_id
        })

    async def get_campaign_stats(self) -> Dict:
        return await self._post("/campaign/stats", {})

    async def get_campaign_responsible_persons(self, campaign_id: str) -> Dict:
        return await self._post("/campaign/responsiblePerson/list", {"campaignID": campaign_id})

    async def create_cloud_meeting(self, room_name: str, is_incognito_allowed: bool = True) -> Dict:
        return await self._post("/cloudMeeting/create", {
            "roomName": room_name,
            "whoCanParticipant": "all",
            "isIncognitoAllowed": "allowed" if is_incognito_allowed else "notAllowed"
        })

    async def start_cloud_meeting(self, meeting_id: str) -> Dict:
        return await self._post("/cloudMeeting/start", {"cloudMeetingID": meeting_id})

    async def join_cloud_meeting(self, meeting_id: str, offer: str, incognito: bool = False, join_mode: str = "normal") -> Dict:
        return await self._post("/cloudMeeting/join", {
            "cloudMeetingID": meeting_id,
            "offer": offer,
            "incognito": incognito,
            "joinMode": join_mode
        })

    async def leave_cloud_meeting(self, meeting_id: str) -> Dict:
        return await self._post("/cloudMeeting/leave", {"cloudMeetingID": meeting_id})

    async def get_cloud_meeting(self, meeting_id: str, is_summary: bool = False) -> Dict:
        return await self._post("/cloudMeeting/get", {
            "cloudMeetingID": meeting_id,
            "isSummary": is_summary
        })

    async def get_meeting_participants(self, meeting_id: str, action: str = "down", participant_id: str = "0", type: str = "all") -> Dict:
        return await self._post("/cloudMeeting/participants/list", {
            "cloudMeetingID": meeting_id,
            "action": action,
            "participantID": participant_id,
            "type": type
        })

    async def request_speak(self, meeting_id: str, raise_hand: bool = True) -> Dict:
        return await self._post("/cloudMeeting/speakRequest", {
            "cloudMeetingID": meeting_id,
            "isRaisedHand": raise_hand
        })

    async def accept_speak_request(self, meeting_id: str, user_id: str) -> Dict:
        return await self._post("/cloudMeeting/speak/set", {
            "cloudMeetingID": meeting_id,
            "userID": user_id,
            "action": "confirm"
        })

    async def reject_speak_request(self, meeting_id: str, user_id: str) -> Dict:
        return await self._post("/cloudMeeting/speak/set", {
            "cloudMeetingID": meeting_id,
            "userID": user_id,
            "action": "reject"
        })

    async def remove_from_speakers(self, meeting_id: str, user_id: str) -> Dict:
        return await self._post("/cloudMeeting/speak/set", {
            "cloudMeetingID": meeting_id,
            "userID": user_id,
            "action": "remove"
        })

    async def kick_from_meeting(self, meeting_id: str, user_id: str) -> Dict:
        return await self._post("/cloudMeeting/kick", {
            "cloudMeetingID": meeting_id,
            "userID": user_id
        })

    async def mute_speaker_by_moderator(self, meeting_id: str, user_id: str, mute: bool = True) -> Dict:
        return await self._post("/cloudMeeting/speak/muteByModerator", {
            "cloudMeetingID": meeting_id,
            "speakerUserID": user_id,
            "action": "mute" if mute else "unmute"
        })

    async def send_meeting_reaction(self, meeting_id: str, reaction: str) -> Dict:
        return await self._post("/cloudMeeting/reaction/set", {
            "cloudMeetingID": meeting_id,
            "reaction": reaction
        })

    async def add_meeting_admin(self, meeting_id: str, user_id: str) -> Dict:
        return await self._post("/cloudMeeting/admin/add", {
            "cloudMeetingID": meeting_id,
            "adminUserID": user_id
        })

    async def remove_meeting_admin(self, meeting_id: str, user_id: str) -> Dict:
        return await self._post("/cloudMeeting/admin/remove", {
            "cloudMeetingID": meeting_id,
            "adminUserID": user_id
        })

    async def get_speak_history(self, meeting_id: str, last_history_id: str = "") -> Dict:
        return await self._post("/cloudMeeting/speak/history", {
            "cloudMeetingID": meeting_id,
            "lastHistoryID": last_history_id
        })

    async def update_cloud_meeting(self, meeting_id: str, room_name: str) -> Dict:
        return await self._post("/cloudMeeting/update", {
            "cloudMeetingID": meeting_id,
            "roomName": room_name
        })

    async def get_ice_config(self) -> Dict:
        return await self._post("/cloudMeeting/getConfig", {})

    async def send_ice_candidates(self, meeting_id: str, candidates: List[str]) -> Dict:
        return await self._post("/cloudMeeting/trickleICE", {
            "cloudMeetingID": meeting_id,
            "ICECandidates": candidates
        })

    async def keep_meeting_alive(self, meeting_id: str) -> Dict:
        return await self._post("/cloudMeeting/keepAlive", {"cloudMeetingID": meeting_id})

    async def mute_mic(self, meeting_id: str, mute: bool = True) -> Dict:
        return await self._post("/cloudMeeting/speak/mute", {
            "cloudMeetingID": meeting_id,
            "action": "mute" if mute else "unmute"
        })

    async def get_user(self, username: str) -> Dict:
        return await self._post("/user/info", {"username": username})

    async def follow_user(self, user_id: str) -> Dict:
        return await self._post("/user/follow", {"followingUserID": user_id, "operation": "follow"})

    async def unfollow_user(self, user_id: str) -> Dict:
        return await self._post("/user/follow", {"followingUserID": user_id, "operation": "unfollow"})

    async def block_user(self, user_id: str, block: bool = True) -> Dict:
        return await self._post("/user/block", {"blockedUserID": user_id, "operation": "block" if block else "unblock"})

    async def mute_user(self, user_id: str, mute: bool = True) -> Dict:
        return await self._post("/user/mute", {"mutedUserID": user_id, "operation": "mute" if mute else "unmute"})

    async def get_followers(self, user_id: str, page: int = 1) -> Dict:
        return await self._post("/user/followers/list", {"userID": user_id, "pageNumber": page})

    async def get_followings(self, user_id: str, page: int = 1) -> Dict:
        return await self._post("/user/followings/list", {"userID": user_id, "pageNumber": page})

    async def get_mutual_followers(self, user_id: str, page: int = 1) -> Dict:
        return await self._post("/user/info/mutualFollowers", {"userID": user_id, "pageNumber": page})

    async def get_blocked_users(self, page: int = 1) -> Dict:
        return await self._post("/user/block/list", {"pageNumber": page})

    async def get_muted_users(self, page: int = 1) -> Dict:
        return await self._post("/user/mute/list", {"pageNumber": page})

    async def search_users(self, query: str, last_user_id: str = "0", location: str = "search-page") -> Dict:
        return await self._post("/search/users", {
            "query": query,
            "lastUserID": last_user_id,
            "location": location
        })

    async def get_suggestions(self, max_items: int = 30) -> Dict:
        return await self._post("/user/suggest/list", {"maxItems": max_items})

    async def update_avatar(self, sid: str) -> Dict:
        return await self._post("/user/avatar/update", {"avatarSID": sid})

    async def remove_avatar(self) -> Dict:
        return await self._post("/user/avatar/remove", {})

    async def update_temporary_avatar(self, avatar_sid: str) -> Dict:
        return await self._post("/user/temporaryAvatar/set", {"avatarSID": avatar_sid})

    async def remove_temporary_avatar(self) -> Dict:
        return await self._post("/user/temporaryAvatar/remove", {})

    async def update_profile(self, bio: str = None, location: str = None, website: str = None,
                             nationality: str = None, account_type: str = None) -> Dict:
        payload = {}
        if bio is not None:
            payload["bio"] = bio
        if location is not None:
            payload["location"] = location
        if website is not None:
            payload["website"] = website
        if nationality is not None:
            payload["nationality"] = nationality
        if account_type is not None:
            payload["accountType"] = account_type
        return await self._post("/user/profile/update", payload)

    async def update_personal_profile(self, firstname: str = None, lastname: str = None,
                                      birth_date: int = None, gender: str = None, job: str = None,
                                      national_id: str = None, national_card_sid: str = None,
                                      professional_doc_sid: str = None) -> Dict:
        payload = {}
        if firstname is not None:
            payload["firstname"] = firstname
        if lastname is not None:
            payload["lastname"] = lastname
        if birth_date is not None:
            payload["birthDate"] = birth_date
        if gender is not None:
            payload["gender"] = gender
        if job is not None:
            payload["job"] = job
        if national_id is not None:
            payload["nationalID"] = national_id
        if national_card_sid is not None:
            payload["nationalCardSID"] = national_card_sid
        if professional_doc_sid is not None:
            payload["professionalAndFamousDocumentSID"] = professional_doc_sid
        return await self._post("/user/profile/personal/update", payload)

    async def update_legal_profile(self, company_name: str = None, brand_name: str = None,
                                   field_of_activity: str = None, work_address: str = None,
                                   national_id: str = None, registration_date: int = None,
                                   registration_cert_sid: str = None, last_changes_cert_sid: str = None,
                                   introduction_letter_sid: str = None, activities_license_sid: str = None) -> Dict:
        payload = {}
        if company_name is not None:
            payload["companyName"] = company_name
        if brand_name is not None:
            payload["brandName"] = brand_name
        if field_of_activity is not None:
            payload["fieldOfActivity"] = field_of_activity
        if work_address is not None:
            payload["workAddress"] = work_address
        if national_id is not None:
            payload["nationalID"] = national_id
        if registration_date is not None:
            payload["registrationDate"] = registration_date
        if registration_cert_sid is not None:
            payload["registrationCertificateSID"] = registration_cert_sid
        if last_changes_cert_sid is not None:
            payload["lastChangesCertificateSID"] = last_changes_cert_sid
        if introduction_letter_sid is not None:
            payload["introductionLetterSID"] = introduction_letter_sid
        if activities_license_sid is not None:
            payload["activitiesLicenseSID"] = activities_license_sid
        return await self._post("/user/profile/legal/update", payload)

    async def update_username(self, new_username: str) -> Dict:
        return await self._post("/user/username/update", {"username": new_username})

    async def check_username_availability(self, username: str) -> Dict:
        return await self._post("/user/username/check", {"username": username})

    async def change_password(self, old_password: str, new_password: str) -> Dict:
        return await self._post("/user/password/set", {
            "oldPassword": old_password,
            "newPassword": new_password
        })

    async def reset_password(self, verified_token: str, new_password: str) -> Dict:
        return await self._post("/user/password/set", {
            "verifiedToken": verified_token,
            "newPassword": new_password
        })

    async def logout_user(self) -> Dict:
        return await self._post("/user/logout", {})

    async def deactivate_account(self) -> Dict:
        return await self._post("/user/deactive", {})

    async def get_sessions(self) -> Dict:
        return await self._post("/device/list", {})

    async def remove_session(self, device_id: str, other: bool = False) -> Dict:
        return await self._post("/device/remove", {"ID": device_id, "other": other})

    async def set_conversation_policy(self, policy_type: str) -> Dict:
        return await self._post("/conversation/policy/set", {"policyType": policy_type})

    async def report_user(self, user_id: str, abuse_category_id: str, description: str) -> Dict:
        return await self._post("/user/abuseReport", {
            "userID": user_id,
            "abuseCategoryID": abuse_category_id,
            "description": description
        })

    async def get_referral_info(self, referral_code: str) -> Dict:
        return await self._post("/user/getUsernameByReferralCode", {"referralCode": referral_code})

    async def join_referral(self, referral_code: str) -> Dict:
        return await self._post("/user/referral/join", {"referralCode": referral_code})

    async def get_conversations(self, action: str = "down", type: str = "confirmed") -> Dict:
        return await self._post("/conversation/list", {
            "action": action,
            "type": type
        })

    async def get_messages(self, user_id: str, action: str = "down", message_id: str = "0") -> Dict:
        return await self._post("/conversation/message/list", {
            "userID": user_id,
            "action": action,
            "messageID": message_id
        })

    async def send_message(self, user_id: str, text: str) -> Dict:
        return await self._post("/conversation/message/send", {
            "userID": user_id,
            "text": text
        })

    async def delete_message(self, user_id: str, message_id: str) -> Dict:
        return await self._post("/conversation/message/remove", {
            "userID": user_id,
            "messageID": message_id
        })

    async def delete_conversation(self, user_id: str) -> Dict:
        return await self._post("/conversation/remove", {
            "userID": user_id
        })

    async def get_conversation_badge(self) -> Dict:
        return await self._post("/conversation/badge", {})

    async def update_conversation_status(self, user_id: str, status: str) -> Dict:
        # status: "confirm", "reject", "spam"
        return await self._post("/conversation/status/update", {
            "userID": user_id,
            "type": status
        })


    async def search_posts(self, query: str, pagination: str = None, method: str = "latest",
                           user_id: str = None, start_date: int = None, end_date: int = None,
                           attachment_types: list = None, topic_ids: list = None,
                           hashtags: list = None, search_type: list = None) -> Dict:
        payload = {"query": query, "method": method}
        if pagination:
            payload["pagination"] = pagination
        if user_id:
            payload["userID"] = user_id
        if start_date:
            payload["startDate"] = start_date
        if end_date:
            payload["endDate"] = end_date
        if attachment_types:
            payload["attachmentTypes"] = attachment_types
        if topic_ids:
            payload["topicIDs"] = topic_ids
        if hashtags:
            payload["hashtags"] = hashtags
        if search_type:
            payload["searchType"] = search_type
        return await self._post("/search/posts", payload)

    async def search_users(self, query: str, last_user_id: str = "0", location: str = "search-page") -> Dict:
        return await self._post("/search/users", {
            "query": query,
            "lastUserID": last_user_id,
            "location": location
        })

    async def get_topics(self) -> Dict:
        return await self._post("/topic/list", {})

    async def add_topic_to_post(self, post_id: str, topic_ids: list) -> Dict:
        return await self._post("/post/topic/add", {
            "postID": post_id,
            "topicIDs": topic_ids
        })

    async def remove_topic_from_post(self, post_id: str, topic_id: str) -> Dict:
        return await self._post("/post/topic/remove", {
            "postID": post_id,
            "topicID": topic_id
        })


    async def get_transactions(self, action: str = "down", currency: str = "IRR", page_id: str = "0") -> Dict:
        return await self._post("/accounting/transactions", {
            "action": action,
            "currency": currency,
            "pageID": page_id
        })

    async def add_fund(self, amount: int, currency: str = "IRR", return_url: str = None) -> Dict:
        payload = {"amount": str(amount), "currency": currency}
        if return_url:
            payload["returnURL"] = return_url
        return await self._post("/accounting/addFund", payload)


    async def get_active_livestreams(self) -> Dict:
        return await self._post("/liveStream/active/list", {})

    async def create_livestream(self, quality: str = "480", record_live: bool = False, cover_sid: str = None) -> Dict:
        payload = {"quality": quality, "recordLive": record_live}
        if cover_sid:
            payload["coverSID"] = cover_sid
        return await self._post("/liveStream/create", payload)


    async def get_general_stats(self) -> Dict:
        return await self._post("/stats", {})

    async def get_user_daily_stats(self, user_id: str) -> Dict:
        return await self._post("/user/stat/daily", {"userID": user_id})


    async def get_short_links(self, entity: str, entity_id: str, action: str = "down", short_link_id: str = "0") -> Dict:
        return await self._post("/shortLink/list", {
            "entity": entity,
            "entityID": entity_id,
            "action": action,
            "shortLinkID": short_link_id
        })

    async def create_short_link(self, entity: str, entity_id: str, title: str = None,
                                max_used_count: int = None, expire_date: int = None,
                                allowed_users: list = None) -> Dict:
        payload = {
            "entity": entity,
            "entityID": entity_id,
        }
        if title:
            payload["title"] = title
        if max_used_count is not None:
            payload["maxUsedCount"] = max_used_count
        if expire_date:
            payload["expireDate"] = expire_date
        if allowed_users:
            payload["allowedUsers"] = allowed_users
        return await self._post("/shortLink/create", payload)

    async def edit_short_link(self, short_link_id: str, title: str = None,
                              max_used_count: int = None, expire_date: int = None,
                              allowed_users: list = None) -> Dict:
        payload = {"shortLinkID": short_link_id}
        if title is not None:
            payload["title"] = title
        if max_used_count is not None:
            payload["maxUsedCount"] = max_used_count
        if expire_date:
            payload["expireDate"] = expire_date
        if allowed_users is not None:
            payload["allowedUsers"] = allowed_users
        return await self._post("/shortLink/edit", payload)

    async def get_short_link_details(self, short_link_id: str) -> Dict:
        return await self._post("/shortLink/get", {"shortLinkID": short_link_id})

    async def remove_short_link(self, short_link_id: str) -> Dict:
        return await self._post("/shortLink/remove", {"shortLinkID": short_link_id})


    async def get_visible_roles(self, section: str) -> Dict:
        return await self._post("/role/visible/list", {"section": section})


    async def get_og_data(self, url: str) -> Dict:
        # OpenGraph fetch (external)
        return await self._get(f"https://og.virasty.com/get?url={url}", base_url="https://og.virasty.com")


    async def get_support_token(self) -> Dict:
        return await self._post("/support/start", {})


    def __repr__(self) -> str:
        if self.auth.is_logged_in:
            return f"VirastyClient(@{self.auth.username})"
        return "VirastyClient(not logged in)"