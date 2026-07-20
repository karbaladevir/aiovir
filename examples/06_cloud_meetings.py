#!/usr/bin/env python3
"""
Example 06: Cloud Meetings (Voice Rooms)
========================================
Create, join, and manage cloud meetings/voice rooms.
"""

import asyncio
import os
from aiovir import VirastyClient


async def meetings_example():
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    print("🎙️ aiovir - Cloud Meetings")
    print("=" * 50)
    
    async with VirastyClient(session_file="session.vir") as client:
        if not client.auth.is_logged_in:
            await client.login(phone, password)
            print(f"✅ Logged in as @{client.auth.username}\n")
        
        # Create meeting
        print("1️⃣  Creating meeting...\n")
        meeting = await client.create_cloud_meeting(
            room_name="🎵 Music Room",
            is_incognito_allowed=True
        )
        
        meeting_data = meeting.get("data", {})
        meeting_id = meeting_data.get("ID", "")
        
        if meeting_id:
            print(f"   ✅ Room: {meeting_data.get('roomName', '')}")
            print(f"   ID: {meeting_id}")
            
            # Start meeting
            print("\n2️⃣  Starting meeting...\n")
            await client.start_cloud_meeting(meeting_id)
            print(f"   ▶️  Started")
            
            await asyncio.sleep(1)
            
            # Get meeting info
            print("\n3️⃣  Meeting info...\n")
            info = await client.get_cloud_meeting(meeting_id, is_summary=True)
            participants = info.get("data", {}).get("participantsCount", 0)
            print(f"   👥 Participants: {participants}")
            
            # Request speak
            print("\n4️⃣  Request speak...\n")
            await client.request_speak(meeting_id, raise_hand=True)
            print(f"   ✋ Hand raised")
            
            # Send reaction
            print("\n5️⃣  Send reaction...\n")
            await client.send_meeting_reaction(meeting_id, "👏")
            print(f"   🎭 Reaction sent")
            
            # Keep alive
            print("\n6️⃣  Keep alive...\n")
            await client.keep_meeting_alive(meeting_id)
            print(f"   💓 Keep alive sent")
            
            # Leave
            await asyncio.sleep(1)
            print("\n7️⃣  Leaving...\n")
            await client.leave_cloud_meeting(meeting_id)
            print(f"   🚪 Left meeting")
        
        # Active meetings
        print("\n8️⃣  Active meetings...\n")
        active = await client.get_active_livestreams()
        count = len(active.get("data", {}).get("items", []))
        print(f"   🟢 Active: {count}")
        
        print("\n✨ Completed!")


if __name__ == "__main__":
    asyncio.run(meetings_example())
