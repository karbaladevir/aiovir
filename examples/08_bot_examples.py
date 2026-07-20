#!/usr/bin/env python3
"""
Example 08: Bot Examples
========================
Auto-reply bot, post scheduler, and simple automation.
"""

import asyncio
import os
from datetime import datetime
from aiovir import VirastyClient


class AutoReplyBot:
    """Auto-reply to direct messages."""
    
    def __init__(self, client, reply_message=None):
        self.client = client
        self.reply_message = reply_message or "👋 Hello! I'm a bot powered by aiovir. I'll reply soon! 🤖"
        self.responded_ids = set()
    
    async def check_and_reply(self):
        conversations = await self.client.get_conversations()
        conv_list = conversations.get("data", {}).get("items", [])
        
        for conv_data in conv_list:
            if conv_data.get("unseenCount", 0) > 0:
                user_id = conv_data.get("userSummary", {}).get("userID")
                
                if user_id in self.responded_ids:
                    continue
                
                messages = await self.client.get_messages(user_id)
                msg_list = messages.get("data", {}).get("items", [])
                
                if msg_list and not msg_list[-1].get("isMine", True):
                    await self.client.send_message(user_id, self.reply_message)
                    self.responded_ids.add(user_id)
                    username = conv_data.get("userSummary", {}).get("username", "?")
                    print(f"   🤖 Replied to @{username}")
    
    async def run(self, interval=30):
        print(f"🤖 Bot started (checking every {interval}s)\nPress Ctrl+C to stop\n")
        try:
            while True:
                await self.check_and_reply()
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 Bot stopped")


class PostScheduler:
    """Schedule posts."""
    
    def __init__(self, client):
        self.client = client
        self.scheduled = []
    
    def schedule(self, text, delay_seconds):
        scheduled_time = datetime.now().timestamp() + delay_seconds
        self.scheduled.append({"text": text, "time": scheduled_time})
        print(f"   ⏰ Scheduled: '{text[:40]}...' in {delay_seconds}s")
    
    async def run(self):
        print("📅 Scheduler started\n")
        while self.scheduled:
            now = datetime.now().timestamp()
            for post in self.scheduled[:]:
                if now >= post["time"]:
                    await self.client.create_post(post["text"])
                    print(f"   ✅ Published: '{post['text'][:40]}...'")
                    self.scheduled.remove(post)
            await asyncio.sleep(1)
        print("   ✅ All published!")


async def run_auto_reply():
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    async with VirastyClient(session_file="session.vir") as client:
        if not client.auth.is_logged_in:
            await client.login(phone, password)
        
        bot = AutoReplyBot(client)
        try:
            await asyncio.wait_for(bot.run(interval=10), timeout=60)
        except asyncio.TimeoutError:
            print("\n⏰ Demo done!")


async def run_scheduler():
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    async with VirastyClient(session_file="session.vir") as client:
        if not client.auth.is_logged_in:
            await client.login(phone, password)
        
        scheduler = PostScheduler(client)
        scheduler.schedule("Post #1 - Hello! 👋", 3)
        scheduler.schedule("Post #2 - Python! 🐍", 6)
        scheduler.schedule("Post #3 - Bye! 👋", 9)
        
        await scheduler.run()


async def main():
    print("Bots available:")
    print("  1. Auto-reply bot")
    print("  2. Post scheduler")
    
    choice = input("\nSelect (1-2): ").strip()
    
    if choice == "1":
        await run_auto_reply()
    elif choice == "2":
        await run_scheduler()
    else:
        print("Invalid!")


if __name__ == "__main__":
    asyncio.run(main())
