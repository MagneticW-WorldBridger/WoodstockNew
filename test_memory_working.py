#!/usr/bin/env python3
"""
Test the working memory backend
"""

import requests
import json

def test_memory():
    """Test memory functionality"""
    base_url = "http://localhost:8001"
    
    print("🧠 Testing Working Memory Backend...")
    
    # Test 1: First message about sectionals
    print("\n📝 Test 1: Asking about sectionals")
    try:
        response1 = requests.post(
            f"{base_url}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "I want to see sectionals"}],
                "user_identifier": "test_user_123"
            }
        )
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Response 1: {result1['choices'][0]['message']['content']}")
        else:
            print(f"❌ Error 1: {response1.status_code} - {response1.text}")
            return
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Test 2: Follow-up asking for picture
    print("\n📝 Test 2: Asking for picture (should remember sectionals)")
    try:
        response2 = requests.post(
            f"{base_url}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Show me the picture"}],
                "user_identifier": "test_user_123"
            }
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Response 2: {result2['choices'][0]['message']['content']}")
            
            # Check if the response shows memory
            if "sectionals" in result2['choices'][0]['message']['content'].lower() or "products" in result2['choices'][0]['message']['content'].lower():
                print("🎉 SUCCESS: Memory is working! The AI remembered you were asking about sectionals!")
            else:
                print("⚠️ Memory might not be working - response doesn't show context")
        else:
            print(f"❌ Error 2: {response2.status_code} - {response2.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 3: Another follow-up
    print("\n📝 Test 3: Asking for more details")
    try:
        response3 = requests.post(
            f"{base_url}/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "What colors are available?"}],
                "user_identifier": "test_user_123"
            }
        )
        
        if response3.status_code == 200:
            result3 = response3.json()
            print(f"✅ Response 3: {result3['choices'][0]['message']['content']}")
            
            # Check if the response shows memory
            if "sectionals" in result3['choices'][0]['message']['content'].lower() or "products" in result3['choices'][0]['message']['content'].lower():
                print("🎉 SUCCESS: Memory is working! The AI remembered the context!")
            else:
                print("⚠️ Memory might not be working - response doesn't show context")
        else:
            print(f"❌ Error 3: {response3.status_code} - {response3.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_memory()
