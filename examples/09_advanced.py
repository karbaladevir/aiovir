#!/usr/bin/env python3
"""
Example 09: Advanced Features
=============================
Proxy, custom DUID, error handling, concurrent requests.
"""

import asyncio
import os
from aiovir import VirastyClient, VirastyDecoder


async def proxy_example():
    print("🌐 Proxy Example")
    print("-" * 30)
    
    try:
        async with VirastyClient(proxy="socks5://127.0.0.1:9050") as client:
            print("   🔒 Connected via SOCKS5 proxy")
            time = await client.get_server_time()
            print(f"   🕐 {time.get('status', 'error')}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    print()


async def custom_duid_example():
    print("🔐 Custom DUID Example")
    print("-" * 30)
    
    decoder = VirastyDecoder(duid="my-custom-duid-123")
    encrypted = decoder.encrypt_to_b64({"action": "test", "data": "hello"})
    print(f"   🔒 Encrypted: {encrypted[:50]}...")
    
    decrypted = decoder.decrypt_b64(encrypted)
    print(f"   🔓 Decrypted: {decrypted}")
    
    # Static methods
    enc = VirastyDecoder.encrypt_with({"hello": "world"}, "my-custom-duid-123")
    dec = VirastyDecoder.decrypt_with(enc, "my-custom-duid-123")
    print(f"   ✅ Static: {dec}")
    print()


async def error_handling_example():
    print("🛡️ Error Handling Example")
    print("-" * 30)
    
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    async with VirastyClient(session_file="session.vir") as client:
        try:
            result = await client.login(phone, password)
            if result:
                print(f"   ✅ Logged in")
        except Exception as e:
            print(f"   ❌ Error: {type(e).__name__}")
        
        try:
            await client.get_post("fake_id")
        except Exception as e:
            print(f"   ⚠️  Caught: {type(e).__name__}")
    print()


async def concurrent_example():
    print("⚡ Concurrent Requests")
    print("-" * 30)
    
    phone = os.getenv("VIRASTY_PHONE", "+989123456789")
    password = os.getenv("VIRASTY_PASSWORD", "your_password")
    
    async with VirastyClient(session_file="session.vir") as client:
        if not client.auth.is_logged_in:
            await client.login(phone, password)
        
        print("   🚀 Running 6 requests...\n")
        
        tasks = [
            client.get_me(),
            client.get_notification_badge(),
            client.get_trends(),
            client.get_server_time(),
            client.get_version(),
            client.get_conversation_badge(),
        ]
        
        start = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end = asyncio.get_event_loop().time()
        
        print(f"   ⏱️  Done in {end - start:.2f}s")
        success = sum(1 for r in results if not isinstance(r, Exception))
        print(f"   ✅ {success}/6 successful")
    print()


async def main():
    print("🔧 aiovir - Advanced Features")
    print("=" * 50)
    print()
    
    examples = {
        "1": ("Proxy", proxy_example),
        "2": ("Custom DUID", custom_duid_example),
        "3": ("Error Handling", error_handling_example),
        "4": ("Concurrent", concurrent_example),
    }
    
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  5. Run All")
    
    choice = input("\nSelect (1-5): ").strip()
    
    if choice == "5":
        for _, (_, func) in examples.items():
            await func()
    elif choice in examples:
        await examples[choice][1]()
    else:
        print("Invalid!")
    
    print("✨ Done!")


if __name__ == "__main__":
    asyncio.run(main())
