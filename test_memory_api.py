#!/usr/bin/env python3
"""
Test the memory API with consistent user identifier
"""

import requests
import json

def test_memory():
    """Test memory functionality with API calls"""
    base_url = "http://localhost:8001"
    
    print("🧠 Testing Memory API...")
    
    # Test 1: First message about sectionals
    print("\n📝 Test 1: Asking about sectionals")
    response1 = requests.post(
        f"{base_url}/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "I want to see sectionals"}],
            "stream": False,
            "user_identifier": "test_user_123"  # Consistent user ID
        }
    )
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"✅ Response 1: {result1['choices'][0]['message']['content']}")
    else:
        print(f"❌ Error 1: {response1.status_code}")
        return
    
    # Test 2: Follow-up asking for picture
    print("\n📝 Test 2: Asking for picture (should remember sectionals)")
    response2 = requests.post(
        f"{base_url}/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Show me the picture"}],
            "stream": False,
            "user_identifier": "test_user_123"  # Same user ID
        }
    )
    
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"✅ Response 2: {result2['choices'][0]['message']['content']}")
        
        # Check if the response shows memory
        if "sectionals" in result2['choices'][0]['message']['content'].lower():
            print("🎉 SUCCESS: Memory is working! The AI remembered you were asking about sectionals!")
        else:
            print("⚠️ Memory might not be working - response doesn't show context")
    else:
        print(f"❌ Error 2: {response2.status_code}")
    
    # Test 3: Another follow-up
    print("\n📝 Test 3: Asking for more details")
    response3 = requests.post(
        f"{base_url}/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "What colors are available?"}],
            "stream": False,
            "user_identifier": "test_user_123"  # Same user ID
        }
    )
    
    if response3.status_code == 200:
        result3 = response3.json()
        print(f"✅ Response 3: {result3['choices'][0]['message']['content']}")
        
        # Check if the response shows memory
        if "sectionals" in result3['choices'][0]['message']['content'].lower():
            print("🎉 SUCCESS: Memory is working! The AI remembered the context!")
        else:
            print("⚠️ Memory might not be working - response doesn't show context")
    else:
        print(f"❌ Error 3: {response3.status_code}")

if __name__ == "__main__":
    test_memory()
