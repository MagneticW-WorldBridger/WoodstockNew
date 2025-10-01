#!/usr/bin/env python3
"""
🔥 CROSS-CHANNEL MEMORY TEST - FULL THROTTLE
Tests immediate memory availability between webchat and phone
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:8001"
TEST_PHONE = "+1-555-999-8888"  # New phone for clean test
TEST_CALL_ID = "aggressive-test-123"

def print_banner(title):
    print(f"\n🔥 {title}")
    print("=" * 60)

def print_step(step, description, status=""):
    print(f"\n{step}. {description} {status}")

def webchat_message(message, step_num):
    """Send webchat message"""
    print_step(step_num, f"WEBCHAT: '{message}'")
    
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
                print(f"✅ April (Web): {reply[:80]}...")
                return True
            else:
                print(f"❌ Bad response: {data}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def phone_call(message, step_num):
    """Send phone call message"""
    print_step(step_num, f"PHONE: '{message}'")
    
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
            
            print(f"✅ April (Phone): {reply[:80]}...")
            print(f"📋 Context: {has_context} ({context_count} messages)")
            return has_context, context_count
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, 0

def check_memory_immediately(step_num, expected_platforms):
    """Check unified memory immediately after interaction"""
    print_step(step_num, "IMMEDIATE MEMORY CHECK")
    
    try:
        response = requests.get(f"{BASE_URL}/v1/memory/unified/{TEST_PHONE}", 
                              timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_messages = data.get('total_messages', 0)
            platforms = data.get('platforms_used', [])
            
            print(f"📊 Total Messages: {total_messages}")
            print(f"📱 Platforms: {platforms}")
            
            # Check if expected platforms are present
            success = all(platform in platforms for platform in expected_platforms)
            
            if success:
                print(f"✅ Cross-channel memory: WORKING")
            else:
                print(f"❌ Missing platforms. Expected: {expected_platforms}, Got: {platforms}")
            
            # Show recent messages
            history = data.get('conversation_history', [])
            if history:
                print(f"📝 Last 3 Messages:")
                for i, msg in enumerate(history[-3:], 1):
                    platform = msg.get('platform_type', 'unknown')
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')[:50]
                    print(f"   {i}. [{platform}] {role}: {content}...")
            
            return success, platforms, total_messages
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False, [], 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, [], 0

def main():
    """Run aggressive cross-channel memory test"""
    print_banner("AGGRESSIVE CROSS-CHANNEL MEMORY TEST")
    print(f"📱 Test Phone: {TEST_PHONE}")
    print(f"🆔 Call ID: {TEST_CALL_ID}")
    print(f"🌐 Server: {BASE_URL}")
    print(f"🎯 Goal: Verify IMMEDIATE memory availability between channels")
    
    success_count = 0
    total_tests = 8
    
    # PHASE 1: Webchat interaction
    print_banner("PHASE 1: WEBCHAT SETUP")
    
    if webchat_message("Hi, I'm Sarah and I'm looking for a gray sectional sofa", "1A"):
        success_count += 1
    
    time.sleep(1)
    
    if webchat_message("I prefer something modern, around $2000", "1B"):
        success_count += 1
    
    # Check memory after webchat
    success, platforms, msg_count = check_memory_immediately("1C", ["webchat"])
    if success:
        success_count += 1
    
    print(f"\n📊 PHASE 1 RESULTS: {platforms}, {msg_count} messages")
    
    # PHASE 2: Phone call with context
    print_banner("PHASE 2: PHONE CALL WITH CONTEXT")
    
    has_context, context_count = phone_call("Hi, I was just on your website looking at sectionals", "2A")
    if has_context and context_count > 0:
        success_count += 1
        print(f"✅ Phone agent has webchat context: {context_count} messages")
    else:
        print(f"❌ Phone agent missing webchat context")
    
    time.sleep(1)
    
    has_context, context_count = phone_call("I'm Sarah, I mentioned I want a gray modern sectional for $2000", "2B")
    if has_context:
        success_count += 1
    
    # Check memory after phone calls
    success, platforms, msg_count = check_memory_immediately("2C", ["webchat", "phone"])
    if success:
        success_count += 1
        print(f"✅ CROSS-CHANNEL MEMORY: Both platforms present")
    else:
        print(f"❌ CROSS-CHANNEL MEMORY: Failed - {platforms}")
    
    print(f"\n📊 PHASE 2 RESULTS: {platforms}, {msg_count} messages")
    
    # PHASE 3: Return to webchat - should have phone context
    print_banner("PHASE 3: WEBCHAT WITH PHONE CONTEXT")
    
    if webchat_message("I just called about the gray sectional. What were my options?", "3A"):
        success_count += 1
    
    # Final memory check
    success, platforms, msg_count = check_memory_immediately("3B", ["webchat", "phone"])
    if success and msg_count >= 6:  # Should have messages from both channels
        success_count += 1
        print(f"✅ FULL CROSS-CHANNEL MEMORY: Working perfectly")
    else:
        print(f"❌ INCOMPLETE MEMORY: {platforms}, {msg_count} messages")
    
    # FINAL RESULTS
    print_banner("FINAL RESULTS")
    print(f"✅ Successful Tests: {success_count}/{total_tests}")
    print(f"📊 Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count >= 7:
        print("🎉 CROSS-CHANNEL MEMORY: WORKING!")
        print("🚀 Ready for voice agent creation!")
        print("📞 Phone calls will have immediate webchat context")
        print("💻 Webchat will have immediate phone context")
    elif success_count >= 5:
        print("⚠️ PARTIAL SUCCESS: Some issues to fix")
    else:
        print("❌ MAJOR ISSUES: Cross-channel memory not working")
    
    print(f"\n🔧 Next Steps:")
    if success_count >= 7:
        print("1. ✅ Create voice agent with your API keys")
        print("2. ✅ Test real phone calls")
        print("3. ✅ Deploy to production")
    else:
        print("1. ❌ Fix cross-channel memory issues")
        print("2. ❌ Debug platform_type handling")
        print("3. ❌ Verify database storage")

if __name__ == "__main__":
    main()




