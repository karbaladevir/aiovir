#!/usr/bin/env python3
"""
Example 03: User Interactions
=============================
Follow, unfollow, block, mute, search, and profile management.
"""

import asyncio
import os
from aiovir import VirastyClient


async def user_interactions():
    """Demonstrate user-related operations."""
    
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    print("👥 aiovir - User Interactions Example")
    print("=" * 50)
    
    async with VirastyClient(session_file="session.vir") as client:
        
        if not client.auth.is_logged_in:
            await client.login(phone, password)
            print(f"✅ Logged in as @{client.auth.username}\n")
        
        # ─── SEARCH USERS ───
        print("1️⃣  Searching users...\n")
        
        for query in ["python", "developer", "opensource"]:
            results = await client.search_users(query)
            users = results.get("data", {}).get("items", [])
            print(f"   🔍 '{query}' - Found {len(users)} users")
            for u in users[:3]:
                print(f"      • @{u.get('username', '?')} - {u.get('displayName', '')}")
            print()
        
        # ─── GET USER INFO ───
        print("2️⃣  Getting user info...\n")
        
        user_info = await client.get_user("virasty")
        user_data = user_info.get("data", {}).get("user", {})
        
        if user_data:
            print(f"   👤 @{user_data.get('username')}")
            print(f"      Followers: {user_data.get('followersCount', 0):,}")
            print(f"      Following: {user_data.get('followingsCount', 0):,}")
        
        # ─── FOLLOW/UNFOLLOW ───
        print("\n3️⃣  Follow/Unfollow...\n")
        
        if user_data:
            user_id = user_data.get("userID")
            
            await client.follow_user(user_id)
            print(f"   ➕ Followed @{user_data.get('username')}")
            await asyncio.sleep(2)
            
            await client.unfollow_user(user_id)
            print(f"   ➖ Unfollowed @{user_data.get('username')}")
        
        # ─── LISTS ───
        print("\n4️⃣  Block & Mute lists...\n")
        
        blocked = await client.get_blocked_users(page=1)
        print(f"   🚫 Blocked: {len(blocked.get('data', {}).get('items', []))}")
        
        muted = await client.get_muted_users(page=1)
        print(f"   🔇 Muted: {len(muted.get('data', {}).get('items', []))}")
        
        # ─── PROFILE ───
        print("\n5️⃣  Profile info...\n")
        
        me = await client.get_me()
        print(f"   @{me.username}")
        print(f"   Location: {me.location or 'Not set'}")
        print(f"   Website: {me.website or 'Not set'}")
        
        # ─── SUGGESTIONS ───
        print("\n6️⃣  Suggestions...\n")
        
        suggestions = await client.get_suggestions(max_items=5)
        suggested = suggestions.get("data", {}).get("items", [])
        print(f"   💡 {len(suggested)} suggested users")
        
        print("\n✨ User interactions example completed!")


if __name__ == "__main__":
    asyncio.run(user_interactions())
