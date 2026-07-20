#!/usr/bin/env python3
"""
Example 05: Polls and Campaigns
==============================
Create polls, vote, manage campaigns.
"""

import asyncio
import os
from datetime import datetime, timedelta
from aiovir import VirastyClient


async def polls_example(client):
    """Poll creation and voting."""
    print("📊 Polls Example")
    print("-" * 30)
    
    expire_time = int((datetime.now() + timedelta(hours=24)).timestamp() * 1000)
    
    poll = await client.create_poll(
        question="Favorite programming language? 💻",
        options=["Python 🐍", "JavaScript ⚡", "Rust 🦀", "Go 🐹"],
        expire_time=expire_time,
        who_can_see="noOne"
    )
    
    poll_data = poll.get("data", {})
    poll_id = poll_data.get("ID", "")
    print(f"   ✅ Created: {poll_data.get('question', '')}")
    print(f"   Options: {len(poll_data.get('pollOptions', []))}")
    
    if poll_id:
        await asyncio.sleep(1)
        options = poll_data.get("pollOptions", [])
        if options:
            await client.vote_poll(poll_id, options[0].get("ID", ""))
            print(f"   🗳️  Voted: {options[0].get('title', '')}")
    
    print()


async def campaigns_example(client):
    """Campaign creation and management."""
    print("🎯 Campaigns Example")
    print("-" * 30)
    
    campaign = await client.create_campaign(
        title="Support Open Source 🚀",
        description="Let's promote open source together!",
        type="technology",
        hashtags=["#OpenSource", "#Community"],
        urls=["https://github.com"]
    )
    
    campaign_data = campaign.get("data", {})
    campaign_id = campaign_data.get("ID", "")
    
    if campaign_id:
        print(f"   ✅ Created: {campaign_data.get('title', '')}")
        
        await asyncio.sleep(1)
        await client.support_campaign(campaign_id)
        print(f"   🤝 Supported campaign")
        
        await asyncio.sleep(1)
        await client.update_campaign_status(campaign_id, "in_progress")
        print(f"   📊 Status updated")
    
    print()


async def main():
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    print("📊🎯 aiovir - Polls & Campaigns")
    print("=" * 50)
    
    async with VirastyClient(session_file="session.vir") as client:
        if not client.auth.is_logged_in:
            await client.login(phone, password)
            print(f"✅ Logged in as @{client.auth.username}\n")
        
        await polls_example(client)
        await campaigns_example(client)
        print("✨ Completed!")


if __name__ == "__main__":
    asyncio.run(main())
