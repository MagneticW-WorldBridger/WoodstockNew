#!/usr/bin/env python3
"""
Simple memory test without external dependencies
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import os

class SimpleMemory:
    def __init__(self):
        self.in_memory_storage = {}
        print("🔧 SimpleMemory initialized (in-memory only)")
    
    async def init_db(self):
        """Initialize memory system"""
        print("✅ Memory system initialized")
    
    async def get_or_create_conversation(self, user_identifier: str, platform_type: str = 'webchat') -> str:
        """Get existing conversation or create new one"""
        key = f"{user_identifier}_{platform_type}"
        if key not in self.in_memory_storage:
            self.in_memory_storage[key] = {
                'conversation_id': str(uuid.uuid4()),
                'messages': []
            }
            print(f"✅ New {platform_type} conversation created: {self.in_memory_storage[key]['conversation_id']}")
        else:
            print(f"📚 Found existing {platform_type} conversation: {self.in_memory_storage[key]['conversation_id']}")
        return self.in_memory_storage[key]['conversation_id']
    
    async def save_user_message(self, conversation_id: str, content: str):
        """Save user message"""
        for key, data in self.in_memory_storage.items():
            if data['conversation_id'] == conversation_id:
                message = {
                    'role': 'user',
                    'content': content,
                    'created_at': datetime.now().isoformat()
                }
                data['messages'].append(message)
                print(f"💾 User message saved: {content[:50]}...")
                return f"in_memory_{len(data['messages'])}"
        return None
    
    async def save_assistant_message(self, conversation_id: str, content: str):
        """Save assistant message"""
        for key, data in self.in_memory_storage.items():
            if data['conversation_id'] == conversation_id:
                message = {
                    'role': 'assistant',
                    'content': content,
                    'created_at': datetime.now().isoformat()
                }
                data['messages'].append(message)
                print(f"💾 Assistant message saved: {content[:50]}...")
                return f"in_memory_{len(data['messages'])}"
        return None
    
    async def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from conversation"""
        for key, data in self.in_memory_storage.items():
            if data['conversation_id'] == conversation_id:
                messages = data['messages'][-limit:]
                simple_messages = []
                for msg in messages:
                    simple_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
                print(f"📚 Loaded {len(simple_messages)} messages")
                return simple_messages
        return []
    
    async def get_unified_conversation_history(self, user_identifier: str, limit: int = 20) -> List[Dict]:
        """Get conversation history for a user"""
        all_messages = []
        for key, data in self.in_memory_storage.items():
            if key.startswith(f"{user_identifier}_"):
                all_messages.extend(data['messages'])
        
        # Sort by timestamp and limit
        all_messages.sort(key=lambda x: x.get('created_at', 0))
        return all_messages[-limit:] if all_messages else []
    
    async def close(self):
        """Close memory system"""
        print("🔚 Memory system closed")

async def test_memory():
    """Test basic memory functionality"""
    try:
        print("🧠 Testing Memory System...")
        
        # Initialize memory
        memory = SimpleMemory()
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
        
        # Test memory persistence
        print("\n🧠 Testing memory persistence...")
        await memory.save_user_message(conversation_id, "Show me the picture")
        print("✅ Second user message saved")
        
        # Get updated messages
        updated_messages = await memory.get_recent_messages(conversation_id)
        print(f"✅ Now have {len(updated_messages)} messages in conversation")
        
        for i, msg in enumerate(updated_messages):
            print(f"  {i+1}. {msg['role']}: {msg['content']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_memory())
