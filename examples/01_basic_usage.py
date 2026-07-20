#!/usr/bin/env python3
"""
Example 01: Basic Usage
=======================
Shows how to login, get profile info, and create a simple post.
"""

import asyncio
import os
from aiovir import VirastyClient


async def basic_usage():
    """Basic workflow: Login, get profile, create post, view notifications."""
    
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    print("🤖 aiovir - Basic Usage Example")
    print("=" * 50)
    
    async with VirastyClient(session_file="session.vir") as client:
        
        # Step 1: Login (automatically skips if session is valid)
        if not client.auth.is_logged_in:
            print("\n📱 Logging in...")
            success = await client.login(phone, password)
            
            if not success:
                print("❌ Login failed! Check your credentials.")
                return
            
            print(f"✅ Logged in as @{client.auth.username}")
        else:
            print(f"✅ Already logged in as @{client.auth.username}")
        
        # Step 2: Get your profile
        print("\n👤 Fetching profile...")
        me = await client.get_me()
        
        print(f"""
        Profile Information:
        ┌─────────────────────────────────
        │ Username:    @{me.username}
        │ Display Name: {me.display_name}
        │ Bio:         {me.bio[:50] if me.bio else "N/A"}
        │ Followers:   {me.followers_count:,}
        │ Following:   {me.following_count:,}
        │ Posts:       {me.posts_count:,}
        │ Verified:    {'✅' if me.is_verified else '❌'}
        │ Profile URL: {me.profile_url}
        └─────────────────────────────────
        """)
        
        # Step 3: Create a test post
        print("\n📝 Creating a test post...")
        
        post_text = (
            "Hello Virasty! 👋\n"
            "This post was created using aiovir - an async Python client for Virasty.\n\n"
            "#aiovir #python #opensource"
        )
        
        result = await client.create_post(post_text)
        
        if result.get("status") == "success":
            post_data = result.get("data", {}).get("post", {})
            post_id = post_data.get("ID", "")
            print(f"✅ Post created successfully!")
            print(f"   Post URL: https://virasty.com/@{me.username}/post/{post_id}")
        else:
            print("❌ Failed to create post")
        
        # Step 4: Check notifications
        print("\n🔔 Checking notifications...")
        badge = await client.get_notification_badge()
        unseen = badge.get("data", {}).get("unseenCount", 0)
        print(f"   Unread notifications: {unseen}")
        
        # Step 5: Get trending topics
        print("\n🔥 Trending topics...")
        trends = await client.get_trends()
        trend_items = trends.get("data", {}).get("items", [])
        
        for i, trend in enumerate(trend_items[:5], 1):
            print(f"   {i}. #{trend.get('hashtag', 'unknown')} - {trend.get('postCount', 0)} posts")
        
        print("\n✨ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(basic_usage())
