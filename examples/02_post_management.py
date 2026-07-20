#!/usr/bin/env python3
"""
Example 02: Post Management
===========================
Complete post operations: create, edit, delete, react, repost, bookmark.
"""

import asyncio
import os
from datetime import datetime
from aiovir import VirastyClient, Post


async def post_management():
    """Demonstrate full post lifecycle management."""
    
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    print("📝 aiovir - Post Management Example")
    print("=" * 50)
    
    async with VirastyClient(session_file="session.vir") as client:
        
        if not client.auth.is_logged_in:
            await client.login(phone, password)
            print(f"✅ Logged in as @{client.auth.username}\n")
        
        # ─── CREATE POSTS ───
        print("1️⃣  Creating different types of posts...\n")
        
        post1 = await client.create_post("Just a simple text post 📝")
        post1_id = post1.get("data", {}).get("post", {}).get("ID", "")
        print(f"   ✅ Simple post created (ID: {post1_id})")
        
        post2 = await client.create_post(
            "Learning Python async programming 🐍\n"
            "#python #async #programming"
        )
        post2_id = post2.get("data", {}).get("post", {}).get("ID", "")
        print(f"   ✅ Hashtag post created (ID: {post2_id})")
        
        post3 = await client.create_post(
            "Only followers can reply 👥",
            reply_policy="following"
        )
        post3_id = post3.get("data", {}).get("post", {}).get("ID", "")
        print(f"   ✅ Restricted post created (ID: {post3_id})")
        
        await asyncio.sleep(2)
        
        # ─── INTERACT WITH POSTS ───
        print("\n2️⃣  Interacting with posts...\n")
        
        if post2_id:
            await client.toggle_reaction(post2_id, "like")
            print(f"   ❤️  Liked post {post2_id}")
            
            await client.repost(post2_id)
            print(f"   🔄 Reposted post {post2_id}")
            
            await client.bookmark(post2_id, add=True)
            print(f"   🔖 Bookmarked post {post2_id}")
        
        # ─── EDIT POST ───
        print("\n3️⃣  Editing a post...\n")
        
        if post1_id:
            edited_text = (
                "This post was EDITED ✏️\n"
                "Edited at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            await client.edit_post(post1_id, edited_text)
            print(f"   ✅ Post {post1_id} edited successfully")
        
        # ─── GET TIMELINE ───
        print("\n4️⃣  Fetching timeline...\n")
        
        me = await client.get_me()
        my_posts = await client.get_user_posts(me.user_id, action="down")
        posts_list = my_posts.get("data", {}).get("items", [])
        
        print(f"   📋 Your recent posts ({len(posts_list)} found):")
        for i, post in enumerate(posts_list[:5], 1):
            post_obj = Post.from_dict(post)
            print(f"   {i}. {post_obj.summary}")
        
        # ─── CLEANUP ───
        print("\n5️⃣  Cleaning up...\n")
        
        for post_id in [post1_id, post2_id, post3_id]:
            if post_id:
                await client.delete_post(post_id)
                print(f"   🗑️  Deleted post {post_id}")
        
        print("\n✨ Post management example completed!")


if __name__ == "__main__":
    asyncio.run(post_management())
