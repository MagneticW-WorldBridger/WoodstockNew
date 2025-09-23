#!/usr/bin/env python3
"""
🎯 MEMORY PERSISTENCE TEST SCRIPT
Tests webchat → phone → webchat memory continuity
"""

import requests
import json
import time
import asyncio

# Configuration
BASE_URL = "http://localhost:8001"
TEST_PHONE = "+1-555-123-4567"
TEST_CALL_ID = "test-call-12345"

def print_header(title):
    print(f"\n🎯 {title}")
    print("=" * 50)

def print_step(step, description):
    print(f"\n{step}. {description}")

def test_webchat_message(message, step_num):
    """Test webchat message"""
    print_step(step_num, f"WEBCHAT: {message}")
    
    payload = {
        "messages": [{"role": "user", "content": message}],
        "user_identifier": TEST_PHONE,
        "platform_type": "webchat",
        "stream": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/chat/completions", 
                               json=payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and data['choices']:
                reply = data['choices'][0].get('message', {}).get('content', 'No content')
                print(f"✅ April: {reply[:100]}...")
                return True
            else:
                print(f"❌ Unexpected response format: {data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_phone_call(message, step_num):
    """Test phone call message"""
    print_step(step_num, f"PHONE CALL: {message}")
    
    payload = {
        "message": message,
        "phone_number": TEST_PHONE,
        "call_id": TEST_CALL_ID
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/phone/chat", 
                               json=payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get('message', 'No message')
            has_context = data.get('has_context', False)
            context_count = data.get('context_messages', 0)
            
            print(f"✅ April (Phone): {reply[:100]}...")
            print(f"📋 Has Context: {has_context} ({context_count} previous messages)")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_otp_verification(otp_code, step_num):
    """Test OTP verification"""
    print_step(step_num, f"OTP VERIFICATION: {otp_code}")
    
    payload = {
        "phone_number": TEST_PHONE,
        "otp_code": otp_code,
        "call_id": TEST_CALL_ID
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/phone/verify-otp", 
                               json=payload, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            verified = data.get('verified', False)
            message = data.get('message', 'No message')
            
            if verified:
                print(f"✅ OTP Verified: {message}")
            else:
                print(f"❌ OTP Failed: {message}")
            return verified
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_unified_memory(step_num):
    """Check unified memory across channels"""
    print_step(step_num, "CHECKING UNIFIED MEMORY")
    
    try:
        response = requests.get(f"{BASE_URL}/v1/memory/unified/{TEST_PHONE}", 
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_messages = data.get('total_messages', 0)
            platforms = data.get('platforms_used', [])
            
            print(f"✅ Total Messages: {total_messages}")
            print(f"✅ Platforms Used: {', '.join(platforms)}")
            
            # Show last few messages
            history = data.get('conversation_history', [])
            if history:
                print(f"📝 Recent Messages:")
                for i, msg in enumerate(history[-4:], 1):
                    platform = msg.get('platform_type', 'unknown')
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')[:60]
                    print(f"   {i}. [{platform}] {role}: {content}...")
            
            return len(platforms) > 1  # Success if multiple platforms
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run complete memory persistence test"""
    print_header("MEMORY PERSISTENCE TEST - LOCAL ENVIRONMENT")
    print(f"📱 Test Phone: {TEST_PHONE}")
    print(f"🆔 Call ID: {TEST_CALL_ID}")
    print(f"🌐 Server: {BASE_URL}")
    
    # Test sequence
    success_count = 0
    total_tests = 7
    
    # Step 1: Initial webchat interaction
    if test_webchat_message("Hi, I'm looking for a sectional sofa for my living room", "STEP 1"):
        success_count += 1
    
    time.sleep(1)
    
    # Step 2: Follow-up webchat
    if test_webchat_message("I prefer neutral colors like beige or gray", "STEP 2"):
        success_count += 1
    
    time.sleep(1)
    
    # Step 3: Phone call starts (should have context)
    if test_phone_call("Hi, I was just looking at sectional sofas on your website", "STEP 3"):
        success_count += 1
    
    time.sleep(1)
    
    # Step 4: OTP verification
    if test_otp_verification("1234", "STEP 4"):
        success_count += 1
    
    time.sleep(1)
    
    # Step 5: Authenticated phone interaction
    if test_phone_call("Can you help me find the sectional I was looking at?", "STEP 5"):
        success_count += 1
    
    time.sleep(1)
    
    # Step 6: Check unified memory
    if check_unified_memory("STEP 6"):
        success_count += 1
    
    time.sleep(1)
    
    # Step 7: Return to webchat (should remember phone call)
    if test_webchat_message("I just called about the sectional sofas. What were the options again?", "STEP 7"):
        success_count += 1
    
    # Final results
    print_header("TEST RESULTS")
    print(f"✅ Successful Tests: {success_count}/{total_tests}")
    print(f"📊 Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED! Memory persistence is working!")
        print("🚀 Ready for voice agent integration!")
    elif success_count >= 5:
        print("⚠️ Most tests passed. Minor issues to fix.")
    else:
        print("❌ Multiple failures. System needs debugging.")
    
    print(f"\n🔧 Next Steps:")
    print(f"1. If tests passed: Create voice agent with API keys")
    print(f"2. If tests failed: Check server logs and fix issues")
    print(f"3. Test with real phone calls using voice agent")

if __name__ == "__main__":
    main()
