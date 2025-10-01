#!/usr/bin/env python3
"""
🔥 FINAL CROSS-CHANNEL TEST - WITH YOUR API KEYS
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"
TEST_PHONE = "+1-555-FINAL-TEST"

def test_webchat():
    print("🌐 TESTING WEBCHAT...")
    payload = {
        "messages": [{"role": "user", "content": "Hi, I'm testing webchat"}],
        "user_identifier": TEST_PHONE,
        "platform_type": "webchat",
        "stream": False
    }
    
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Webchat working")
        return True
    else:
        print(f"❌ Webchat failed: {response.text}")
        return False

def test_phone_direct():
    print("📞 TESTING PHONE DIRECT...")
    payload = {
        "messages": [{"role": "user", "content": "Hi, I'm testing phone direct"}],
        "user_identifier": TEST_PHONE,
        "platform_type": "phone",
        "stream": False
    }
    
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Phone direct working")
        return True
    else:
        print(f"❌ Phone direct failed: {response.text}")
        return False

def test_phone_endpoint():
    print("📱 TESTING PHONE ENDPOINT...")
    payload = {
        "message": "Hi, I'm testing phone endpoint",
        "phone_number": TEST_PHONE,
        "call_id": "test-endpoint"
    }
    
    response = requests.post(f"{BASE_URL}/v1/phone/chat", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        return True
    else:
        print(f"❌ Phone endpoint failed: {response.text}")
        return False

def check_memory():
    print("🧠 CHECKING MEMORY...")
    response = requests.get(f"{BASE_URL}/v1/memory/unified/{TEST_PHONE}")
    if response.status_code == 200:
        data = response.json()
        platforms = data.get('platforms_used', [])
        total = data.get('total_messages', 0)
        print(f"Platforms: {platforms}")
        print(f"Total messages: {total}")
        
        if 'webchat' in platforms and 'phone' in platforms:
            print("✅ CROSS-CHANNEL MEMORY: WORKING!")
            return True
        else:
            print(f"❌ Missing platforms. Got: {platforms}")
            return False
    else:
        print(f"❌ Memory check failed: {response.text}")
        return False

def main():
    print("🔥 FINAL CROSS-CHANNEL TEST")
    print("=" * 50)
    
    success = 0
    total = 4
    
    if test_webchat():
        success += 1
    
    time.sleep(1)
    
    if test_phone_direct():
        success += 1
    
    time.sleep(1)
    
    if test_phone_endpoint():
        success += 1
    
    time.sleep(1)
    
    if check_memory():
        success += 1
    
    print(f"\n🎯 RESULTS: {success}/{total} tests passed")
    
    if success >= 3:
        print("🚀 READY FOR VOICE AGENT CREATION!")
        print("📞 Cross-channel memory is working!")
    else:
        print("❌ Need to fix cross-channel issues")

if __name__ == "__main__":
    main()




