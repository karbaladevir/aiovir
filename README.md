
<p align="center">
  <img src="https://karbaladevir.github.io/aiovir-docs/assets/logo.jpg" alt="aiovir logo" width="200">
</p>

<h1 align="center">aiovir 🚀</h1>

<p align="center">
  <b>کتابخانه Async پایتون برای Virasty</b><br>
  ساخت ربات، سلف‌کلاینت، ابزارهای اتوماسیون و یکپارچه‌سازی با Virasty
</p>

<p align="center">
  <a href="https://pypi.org/project/aiovir/">
    <img src="https://img.shields.io/pypi/v/aiovir?color=blue" alt="PyPI">
  </a>
  <a href="https://pypi.org/project/aiovir/">
    <img src="https://img.shields.io/pypi/pyversions/aiovir" alt="Python">
  </a>
  <a href="https://github.com/karbaladevir/aiovir/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/karbaladevir/aiovir" alt="License">
  </a>
  <a href="https://karbaladevir.github.io/aiovir-docs/">
    <img src="https://img.shields.io/badge/docs-مستندات-purple" alt="Docs">
  </a>
</p>

---

## 📖 مستندات

مستندات کامل در **[karbaladevir.github.io/aiovir-docs](https://karbaladevir.github.io/aiovir-docs/)** در دسترس است.

---

## 📦 نصب

```bash
pip install aiovir
```

با پشتیبانی پروکسی:

```bash
pip install aiovir[proxy]
```

---

## 🚀 شروع سریع

```python
import asyncio
from aiovir import VirastyClient

async def main():
    async with VirastyClient(session_file="bot.vir") as client:
        await client.login("09123456789", "password")
        me = await client.get_me()
        print(f"سلام @{me.username}")

asyncio.run(main())
```

---

## 🏗️ سازنده (Constructor)

### `VirastyClient`

```python
from aiovir import VirastyClient

client = VirastyClient(
    token=None,           # str | None - توکن دستی (اختیاری)
    session_file=None,    # str | None - مسیر فایل نشست
    duid=None,            # str | None - شناسه دستگاه
    proxy=None            # str | None - آدرس پروکسی (socks5:// یا http://)
)
```

| پارامتر | نوع | پیش‌فرض | توضیح |
|---------|------|---------|--------|
| `token` | `Optional[str]` | `None` | توکن دسترسی دستی |
| `session_file` | `Optional[str]` | `None` | مسیر فایل نشست. پیش‌فرض: `~/.aiovir/session.vir` |
| `duid` | `Optional[str]` | `None` | شناسه دستگاه (Device Unique ID) |
| `proxy` | `Optional[str]` | `None` | آدرس پروکسی به فرمت `socks5://127.0.0.1:9050` |

---

## 📚 متدهای کامل

### 🔑 احراز هویت و هسته کلاینت

| متد | توضیح |
|------|-----------|
| `login(username, password)` | ورود با شماره موبایل و رمز عبور. نشست خودکار ذخیره می‌شود |
| `logout()` | پاکسازی نشست جاری از حافظه |
| `logout_user()` | خروج از حساب کاربری در سرور |
| `get_me()` | دریافت اطلاعات کاربر لاگین‌شده (برمی‌گرداند `User`) |
| `get_version()` | دریافت نسخه API |
| `get_server_time()` | دریافت زمان سرور |
| `get_general_stats()` | آمار کلی پلتفرم |
| `get_support_token()` | دریافت توکن پشتیبانی |
| `get_visible_roles(section)` | لیست رول‌های قابل مشاهده |

---

### 👤 حساب کاربری و پروفایل

| متد | توضیح |
|------|-----------|
| `get_user(username)` | دریافت اطلاعات کاربر با نام کاربری |
| `update_profile(bio, location, website, nationality, account_type)` | به‌روزرسانی بیو، موقعیت و وب‌سایت |
| `update_personal_profile(firstname, lastname, birth_date, gender, job, ...)` | ویرایش اطلاعات شخصی |
| `update_legal_profile(company_name, brand_name, ...)` | ویرایش اطلاعات حقوقی |
| `update_username(new_username)` | تغییر نام کاربری |
| `check_username_availability(username)` | بررسی آزاد بودن نام کاربری |
| `change_password(old_password, new_password)` | تغییر رمز عبور |
| `reset_password(verified_token, new_password)` | بازنشانی رمز با توکن |
| `update_avatar(sid)` | تغییر آواتار |
| `remove_avatar()` | حذف آواتار |
| `update_temporary_avatar(avatar_sid)` | تنظیم آواتار موقت |
| `remove_temporary_avatar()` | حذف آواتار موقت |
| `deactivate_account()` | غیرفعال‌سازی حساب |
| `get_sessions()` | لیست نشست‌های فعال |
| `remove_session(device_id, other=False)` | حذف نشست دستگاه |
| `get_referral_info(referral_code)` | اطلاعات کد معرف |
| `join_referral(referral_code)` | ثبت کد معرف |
| `get_user_daily_stats(user_id)` | آمار روزانه کاربر |

---

### 📝 پست‌ها و ویراست‌ها

| متد | توضیح |
|------|-----------|
| `create_post(text, media, reply_post_id, root_post_id, thread_root_post_id, reply_policy, community_id, poll_id, campaign_id, cloud_meeting_id, live_stream_id, title, extra_data, **kwargs)` | ایجاد پست جدید |
| `get_post(post_id)` | دریافت پست با شناسه |
| `edit_post(post_id, text, title, styles)` | ویرایش پست |
| `delete_post(post_id)` | حذف پست |
| `get_user_posts(user_id, post_id="0", action="down", type="posts")` | دریافت پست‌های کاربر |
| `toggle_reaction(post_id, reaction)` | ثبت/حذف واکنش (like, love, haha, wow, sad, angry) |
| `repost(post_id)` | بازنشر پست |
| `undo_repost(post_id)` | لغو بازنشر |
| `bookmark(post_id, add=True)` | افزودن/حذف نشانه |
| `pin_post(post_id, pin=True)` | سنجاق/برداشتن سنجاق پست |
| `report_post(post_id, abuse_category_id, description)` | گزارش تخلف پست |
| `get_replies(post_id, action="down", last_post_id="0", order="asc")` | لیست پاسخ‌های پست |
| `get_reposts(post_id, page=1)` | لیست بازنشرکنندگان |
| `get_repost_quotes(post_id, page=1)` | لیست بازنشرهای همراه متن |
| `get_reactioners(post_id, page=1)` | لیست واکنش‌دهندگان |
| `get_post_stats(post_id)` | آمار پست |
| `update_post_rating(post_id, score, direction="increase")` | امتیازدهی به پست |
| `mute_post_mentions(post_id, mute=True)` | بی‌صدا کردن منشن‌های پست |
| `get_edit_history(post_id)` | تاریخچه ویرایش‌های پست |
| `set_post_title(post_id, title)` | تنظیم عنوان پست |
| `remove_post_title(post_id)` | حذف عنوان پست |
| `add_media_to_post(post_id, media_sid, caption="", cover_sid="", url="")` | افزودن رسانه به پست |
| `remove_media_from_post(post_id, media_sid, dont_remove_post=False)` | حذف رسانه از پست |
| `update_media_caption(post_media_id, caption, url="", cover_sid="")` | ویرایش کپشن رسانه |
| `fact_check_post(post_id, fact_type)` | برچسب راستی‌آزمایی |

---

### 📊 فید و تایم‌لاین

| متد | توضیح |
|------|-----------|
| `get_feed(action="", post_id="0", type=None, attachment_type=None, topic_id=None)` | فید اصلی |
| `get_feed_for_you(pagination=None)` | فید پیشنهادی |
| `get_feed_update(type, attachment_type, topic_id)` | بروزرسانی فید |
| `get_public_feed()` | فید عمومی |
| `get_trends()` | موضوعات داغ |
| `get_bookmarks(action="down", bookmark_id="0")` | لیست نشانه‌ها |
| `clear_bookmarks()` | پاکسازی نشانه‌ها |

---

### 🔔 اعلان‌ها

| متد | توضیح |
|------|-----------|
| `get_notification_badge()` | تعداد اعلان‌های خوانده‌نشده |
| `get_notifications(page_size=50, action="down", notification_id="0", seen=None)` | لیست اعلان‌ها |
| `mark_all_notifications_read()` | علامت‌گذاری همه به عنوان خوانده‌شده |
| `clear_all_notifications()` | پاکسازی همه اعلان‌ها |

---

### 💬 پیام خصوصی

| متد | توضیح |
|------|-----------|
| `get_conversations(action="down", type="confirmed")` | لیست مکالمات |
| `get_messages(user_id, action="down", message_id="0")` | پیام‌های یک مکالمه |
| `send_message(user_id, text)` | ارسال پیام |
| `delete_message(user_id, message_id)` | حذف پیام |
| `delete_conversation(user_id)` | حذف مکالمه |
| `get_conversation_badge()` | تعداد پیام‌های نخوانده |
| `update_conversation_status(user_id, status)` | تغییر وضعیت مکالمه (confirm/reject/spam) |
| `set_conversation_policy(policy_type)` | تنظیم سیاست پیام‌ها |

---

### 👥 تعاملات کاربران

| متد | توضیح |
|------|-----------|
| `follow_user(user_id)` | دنبال کردن |
| `unfollow_user(user_id)` | لغو دنبال کردن |
| `block_user(user_id, block=True)` | بلاک/آنبلاک |
| `mute_user(user_id, mute=True)` | میوت/آنمیوت |
| `get_followers(user_id, page=1)` | لیست دنبال‌کنندگان |
| `get_followings(user_id, page=1)` | لیست دنبال‌شوندگان |
| `get_mutual_followers(user_id, page=1)` | دنبال‌کنندگان متقابل |
| `get_blocked_users(page=1)` | لیست بلاک‌شده‌ها |
| `get_muted_users(page=1)` | لیست میوت‌شده‌ها |
| `search_users(query, last_user_id="0", location="search-page")` | جستجوی کاربران |
| `get_suggestions(max_items=30)` | پیشنهاد کاربران |
| `report_user(user_id, abuse_category_id, description)` | گزارش تخلف کاربر |

---

### 📊 نظرسنجی

| متد | توضیح |
|------|-----------|
| `create_poll(question, options, expire_time, who_can_see="noOne")` | ایجاد نظرسنجی |
| `vote_poll(poll_id, option_id)` | رأی دادن |
| `retract_vote(poll_id)` | لغو رأی |
| `get_poll_participants(poll_id, action="down", page_id="0")` | لیست شرکت‌کنندگان |

---

### 🎯 کمپین

| متد | توضیح |
|------|-----------|
| `create_campaign(title, description, type, hashtags, responsible_persons, urls)` | ایجاد کمپین |
| `support_campaign(campaign_id)` | حمایت از کمپین |
| `update_campaign_status(campaign_id, status, description, importance_factor)` | بروزرسانی وضعیت |
| `update_campaign(campaign_id, title, description, type, responsible_persons)` | ویرایش کمپین |
| `get_campaign_followups(campaign_followup_user_id="0", action="down")` | پیگیری‌های کمپین |
| `add_campaign_followup(campaign_id, user_id)` | افزودن پیگیر |
| `remove_campaign_followup(campaign_id, user_id)` | حذف پیگیر |
| `add_followup_result(campaign_id, post_id)` | افزودن نتیجه پیگیری |
| `remove_followup_result(campaign_id, post_id)` | حذف نتیجه پیگیری |
| `get_campaign_stats()` | آمار کمپین‌ها |
| `get_campaign_responsible_persons(campaign_id)` | مسئولین کمپین |

---

### 🎙️ اتاق صوتی (Cloud Meeting)

| متد | توضیح |
|------|-----------|
| `create_cloud_meeting(room_name, is_incognito_allowed=True)` | ایجاد اتاق |
| `start_cloud_meeting(meeting_id)` | شروع اتاق |
| `join_cloud_meeting(meeting_id, offer, incognito=False, join_mode="normal")` | ورود به اتاق |
| `leave_cloud_meeting(meeting_id)` | خروج از اتاق |
| `get_cloud_meeting(meeting_id, is_summary=False)` | اطلاعات اتاق |
| `get_meeting_participants(meeting_id, action="down", participant_id="0", type="all")` | لیست شرکت‌کنندگان |
| `request_speak(meeting_id, raise_hand=True)` | درخواست صحبت |
| `accept_speak_request(meeting_id, user_id)` | تأیید درخواست صحبت |
| `reject_speak_request(meeting_id, user_id)` | رد درخواست صحبت |
| `remove_from_speakers(meeting_id, user_id)` | حذف از سخنرانان |
| `kick_from_meeting(meeting_id, user_id)` | اخراج از اتاق |
| `mute_speaker_by_moderator(meeting_id, user_id, mute=True)` | میوت توسط مدیر |
| `send_meeting_reaction(meeting_id, reaction)` | ارسال واکنش |
| `add_meeting_admin(meeting_id, user_id)` | افزودن مدیر |
| `remove_meeting_admin(meeting_id, user_id)` | حذف مدیر |
| `get_speak_history(meeting_id, last_history_id="")` | تاریخچه سخنرانان |
| `update_cloud_meeting(meeting_id, room_name)` | ویرایش نام اتاق |
| `get_ice_config()` | دریافت کانفیگ ICE |
| `send_ice_candidates(meeting_id, candidates)` | ارسال کاندیداهای ICE |
| `keep_meeting_alive(meeting_id)` | زنده نگه‌داشتن اتصال |
| `mute_mic(meeting_id, mute=True)` | قطع/وصل میکروفون |

---

### 🔍 جستجو و موضوعات

| متد | توضیح |
|------|-----------|
| `search_posts(query, pagination, method, user_id, start_date, end_date, attachment_types, topic_ids, hashtags, search_type)` | جستجوی پیشرفته پست |
| `search_users(query, last_user_id="0", location="search-page")` | جستجوی کاربران |
| `get_topics()` | لیست موضوعات |
| `add_topic_to_post(post_id, topic_ids)` | افزودن موضوع به پست |
| `remove_topic_from_post(post_id, topic_id)` | حذف موضوع از پست |

---

### 🔗 لینک کوتاه

| متد | توضیح |
|------|-----------|
| `get_short_links(entity, entity_id, action="down", short_link_id="0")` | لیست لینک‌های کوتاه |
| `create_short_link(entity, entity_id, title, max_used_count, expire_date, allowed_users)` | ایجاد لینک کوتاه |
| `edit_short_link(short_link_id, title, max_used_count, expire_date, allowed_users)` | ویرایش لینک کوتاه |
| `get_short_link_details(short_link_id)` | جزئیات لینک |
| `remove_short_link(short_link_id)` | حذف لینک |

---

### 💰 امور مالی

| متد | توضیح |
|------|-----------|
| `get_transactions(action="down", currency="IRR", page_id="0")` | لیست تراکنش‌ها |
| `add_fund(amount, currency="IRR", return_url=None)` | افزایش اعتبار |

---

### 📡 سایر

| متد | توضیح |
|------|-----------|
| `get_active_livestreams()` | لایوهای فعال |
| `create_livestream(quality="480", record_live=False, cover_sid=None)` | ایجاد لایو |
| `get_og_data(url)` | دریافت متادیتای OpenGraph |

---
## 🔐 راهنمای DUID (Device Unique ID)

### DUID چیست؟
**DUID** یک شناسه منحصربه‌فرد برای دستگاه شماست که Virasty از آن برای رمزنگاری ارتباطات استفاده می‌کند. هر درخواست به API با کلید AES مشتق‌شده از ۱۶ بایت اول DUID رمزنگاری می‌شود.

⚠️ **هشدار مهم:** اگر DUID اشتباه باشد، کتابخانه **کار نمی‌کند** — سرور نمی‌تواند درخواست شما را رمزگشایی کند و با خطا مواجه می‌شوید.

### چگونه DUID خود را پیدا کنید؟
1. مرورگر را باز کنید و وارد **Virasty** شوید
2. **F12** را بزنید و به تب **Network** بروید
3. یک درخواست به `api.virasty.com` پیدا کنید (مثلاً `/time/now`)
4. در **Request Headers** به دنبال فیلد `duid` بگردید
5. مقدار آن را کپی کنید (چیزی شبیه `1jtbfnd001f4je-web`)

### تنظیم DUID در aiovir
```python
# روش ۱: هنگام ساخت کلاینت
client = VirastyClient(duid="duid-شما")

# روش ۲: با متد set_duid
from aiovir import VirastyDecoder
decoder = VirastyDecoder()
decoder.set_duid("duid-شما")

# روش ۳: تغییر DUID پیش‌فرض (دائمی)
from aiovir import VirastyDecoder
VirastyDecoder.DEFAULT_DUID = "duid-شما"

## 📦 مدل‌های داده

### `User`
```python
from aiovir import User
user = User.from_dict(data)
# Attributes: user_id, username, display_name, bio, avatar, followers_count, 
#             following_count, posts_count, is_verified, profile_url, mention, full_name
```

### `Post`
```python
from aiovir import Post
post = Post.from_dict(data)
# Attributes: post_id, text, post_type, media_type, replies_count, reposts_count,
#             reactions_count, created_datetime, url, summary, is_reply, is_repost,
#             has_media, has_poll, hashtags, mentions
```

### `Notification`
```python
from aiovir import Notification
notif = Notification.from_dict(data)
# Attributes: notification_id, notification_type, is_read, actor, post, 
#             type_emoji, description, created_datetime
```

### `Conversation`
```python
from aiovir import Conversation
conv = Conversation.from_dict(data)
# Attributes: conversation_id, user, last_message, unread_count, is_confirmed
```

### `Message`
```python
from aiovir import Message
msg = Message.from_dict(data)
# Attributes: message_id, text, sender_id, is_mine, created_datetime
```

### `Poll`
```python
from aiovir import Poll
poll = Poll.from_dict(data)
# Attributes: poll_id, question, options, total_votes, is_expired, results
```

### `Campaign`
```python
from aiovir import Campaign
campaign = Campaign.from_dict(data)
# Attributes: campaign_id, title, description, campaign_type, supporter_count
```

### `CloudMeeting`
```python
from aiovir import CloudMeeting
meeting = CloudMeeting.from_dict(data)
# Attributes: meeting_id, room_name, status, participants_count, is_active
```

---
## 🌐 جامعه کاربران

- **[تلگرام](https://t.me/aiovir)** — کانال رسمی تلگرام
- **[بله](https://ble.ir/aiovir)** — کانال رسمی بله
- **[ گروه بله](https://ble.ir/aiovirgp)** — کانال رسمی بله
- **[مستندات](https://karbaladevir.github.io/aiovir-docs/)** — مستندات کامل

## 👥 توسعه‌دهندگان

- **[Kheybar](https://ble.ir/yabercif)** — توسعه‌دهنده
- **[Amirali](https://ble.ir/amirali_khosravinejad)** — توسعه‌دهنده
- **[Saman Rezaei](https://ble.ir/Linus_Torvalds)** — توسعه‌دهنده
---

## 📄 مجوز

MIT License — استفاده آزاد در پروژه‌های تجاری

## ⚠️ سلب مسئولیت

این کتابخانه غیررسمی است. لطفاً قوانین Virasty را رعایت کنید.

---

<p align="center">
 گرداوری شده توسط تیم در راه کربلا  | karbaladev.ir
</p>
