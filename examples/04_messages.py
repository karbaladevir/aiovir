#!/usr/bin/env python3
"""
Example 04: Direct Messages
===========================
Send, receive, and manage direct messages and conversations.
"""

import asyncio
import os
from aiovir import VirastyClient, Conversation, Message


async def messages_example():
    """Demonstrate messaging features."""
    
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    print("💬 aiovir - Messages Example")
    print("=" * 50)
    
    async with VirastyClient(session_file="session.vir") as client:
        
        if not client.auth.is_logged_in:
            await client.login(phone, password)
            print(f"✅ Logged in as @{client.auth.username}\n")
        
        # ─── GET CONVERSATIONS ───
        print("1️⃣  Getting conversations...\n")
        
        conversations = await client.get_conversations(type="confirmed")
        conv_list = conversations.get("data", {}).get("items", [])
        
        print(f"   📨 Confirmed: {len(conv_list)}")
        
        for conv_data in conv_list[:5]:
            conv = Conversation.from_dict(conv_data)
            badge = f"🔴 {conv.unread_count}" if conv.unread_count > 0 else ""
            print(f"      • {conv} {badge}")
        
        # ─── PENDING ───
        pending = await client.get_conversations(type="pending")
        print(f"\n   📩 Pending: {len(pending.get('data', {}).get('items', []))}")
        
        # ─── READ MESSAGES ───
        if conv_list:
            print("\n2️⃣  Reading messages...\n")
            
            first_conv = Conversation.from_dict(conv_list[0])
            
            if first_conv.user:
                messages = await client.get_messages(first_conv.user.user_id, action="down")
                msg_list = messages.get("data", {}).get("items", [])
                print(f"   📝 {len(msg_list)} messages")
                
                for msg_data in msg_list[-3:]:
                    msg = Message.from_dict(msg_data)
                    sender = "You" if msg.is_mine else first_conv.user.username
                    print(f"      {sender}: {msg.text[:40]}...")
        
        # ─── SEND MESSAGE ───
        if conv_list and first_conv.user:
            print("\n3️⃣  Sending message...\n")
            
            result = await client.send_message(
                first_conv.user.user_id,
                "Hello! 👋 Sent via aiovir! 😎"
            )
            print(f"   ✅ Sent: {result.get('status', 'error')}")
        
        # ─── BADGE ───
        print("\n4️⃣  Message badge...\n")
        
        badge = await client.get_conversation_badge()
        print(f"   📬 Unread: {badge.get('data', {}).get('unreadCount', 0)}")
        
        print("\n✨ Messages example completed!")


if __name__ == "__main__":
    asyncio.run(messages_example())
