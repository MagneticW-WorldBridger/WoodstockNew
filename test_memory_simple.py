#!/usr/bin/env python3
"""
Simple test to verify memory functionality
"""

import asyncio
import os
from backend.conversation_memory import memory

async def test_memory():
    """Test basic memory functionality"""
    try:
        print("🧠 Testing Memory System...")
        
        # Check if DATABASE_URL is set
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not set!")
            return False
        
        print(f"✅ DATABASE_URL: {db_url[:20]}...")
        
        # Initialize memory
        await memory.init_db()
        print("✅ Memory system initialized")
        
        # Test conversation creation
        test_user = "test_user_123"
        conversation_id = await memory.get_or_create_conversation(test_user)
        print(f"✅ Conversation created: {conversation_id}")
        
        # Test saving messages
        await memory.save_user_message(conversation_id, "Hello, I want to see products")
        print("✅ User message saved")
        
        await memory.save_assistant_message(conversation_id, "I'll help you find products. What are you looking for?")
        print("✅ Assistant message saved")
        
        # Test retrieving messages
        messages = await memory.get_recent_messages(conversation_id)
        print(f"✅ Retrieved {len(messages)} messages")
        
        for msg in messages:
            print(f"  - {msg['role']}: {msg['content'][:50]}...")
        
        # Test conversation history
        history = await memory.get_unified_conversation_history(test_user)
        print(f"✅ Retrieved {len(history)} messages from history")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False
    finally:
        await memory.close()

if __name__ == "__main__":
    asyncio.run(test_memory())
