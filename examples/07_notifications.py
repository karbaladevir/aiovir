#!/usr/bin/env python3
"""
Example 07: Notifications
========================
Handle notifications, mark as read, clear all.
"""

import asyncio
import os
from aiovir import VirastyClient, Notification


async def notifications_example():
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    print("🔔 aiovir - Notifications")
    print("=" * 50)
    
    async with VirastyClient(session_file="session.vir") as client:
        if not client.auth.is_logged_in:
            await client.login(phone, password)
            print(f"✅ Logged in as @{client.auth.username}\n")
        
        # Badge
        print("1️⃣  Badge...\n")
        badge = await client.get_notification_badge()
        unseen = badge.get("data", {}).get("unseenCount", 0)
        print(f"   🔴 Unseen: {unseen}")
        
        # Get notifications
        print("\n2️⃣  Getting notifications...\n")
        notifications = await client.get_notifications(page_size=10, action="down")
        items = notifications.get("data", {}).get("items", [])
        print(f"   📬 {len(items)} notifications:")
        
        for i, n in enumerate(items[:5], 1):
            notif = Notification.from_dict(n)
            is_new = "🔵" if not notif.is_read else "⚪"
            actor = f"@{notif.actor.username}" if notif.actor else "?"
            print(f"   {i}. {is_new} {notif.type_emoji} {notif.notification_type} from {actor}")
        
        # Mark all read
        print("\n3️⃣  Mark all read...\n")
        await client.mark_all_notifications_read()
        print(f"   ✅ Done")
        
        # Check badge again
        badge_after = await client.get_notification_badge()
        print(f"   🔴 After: {badge_after.get('data', {}).get('unseenCount', 0)}")
        
        print("\n✨ Completed!")


if __name__ == "__main__":
    asyncio.run(notifications_example())
