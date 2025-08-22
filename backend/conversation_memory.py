"""
Simple Conversation Memory using EXISTING PostgreSQL tables
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import asyncpg
import os
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart, TextPart

class SimpleMemory:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.pool = None
        print("🔧 SimpleMemory initialized")
    
    async def init_db(self):
        """Initialize database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=3)
            print("✅ PostgreSQL pool initialized")
    
    async def get_or_create_conversation(self, user_identifier: str) -> str:
        """Get existing conversation or create new one"""
        try:
            async with self.pool.acquire() as conn:
                # Get existing active conversation
                conversation = await conn.fetchrow("""
                    SELECT conversation_id FROM chatbot_conversations 
                    WHERE user_identifier = $1 AND platform_type = 'webchat' AND is_active = true
                    ORDER BY last_message_at DESC
                    LIMIT 1
                """, user_identifier)
                
                if conversation:
                    conv_id = str(conversation['conversation_id'])
                    print(f"📚 Found existing conversation: {conv_id}")
                    return conv_id
                
                # Create new conversation
                conversation_id = await conn.fetchval("""
                    INSERT INTO chatbot_conversations (user_identifier, platform_type)
                    VALUES ($1, 'webchat')
                    RETURNING conversation_id
                """, user_identifier)
                
                conv_id = str(conversation_id)
                print(f"✅ New conversation created: {conv_id}")
                return conv_id
                
        except Exception as e:
            print(f"❌ Error managing conversation: {e}")
            return str(uuid.uuid4())
    
    async def save_user_message(self, conversation_id: str, content: str):
        """Save user message"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO chatbot_messages (conversation_id, message_role, message_content)
                    VALUES ($1, 'user', $2)
                """, conversation_id, content)
                print(f"💾 User message saved")
        except Exception as e:
            print(f"❌ Error saving user message: {e}")
    
    async def save_assistant_message(self, conversation_id: str, content: str, 
                                   function_name: Optional[str] = None,
                                   function_args: Optional[Dict] = None,
                                   function_result: Optional[Any] = None):
        """Save assistant message with optional function data"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO chatbot_messages (
                        conversation_id, message_role, message_content,
                        executed_function_name, function_input_parameters, function_output_result
                    ) VALUES ($1, 'assistant', $2, $3, $4, $5)
                """, 
                    conversation_id, content, function_name,
                    json.dumps(function_args) if function_args else None,
                    json.dumps(function_result) if function_result else None
                )
                print(f"💾 Assistant message saved")
        except Exception as e:
            print(f"❌ Error saving assistant message: {e}")
    
    async def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from conversation"""
        try:
            async with self.pool.acquire() as conn:
                messages = await conn.fetch("""
                    SELECT 
                        message_role,
                        message_content,
                        executed_function_name,
                        function_input_parameters,
                        function_output_result,
                        message_created_at
                    FROM chatbot_messages 
                    WHERE conversation_id = $1
                    ORDER BY message_created_at ASC
                    LIMIT $2
                """, conversation_id, limit)
                
                # Convert to simple format for PydanticAI
                simple_messages = []
                for msg in messages:
                    # Only add user and assistant messages to history
                    if msg['message_role'] in ['user', 'assistant']:
                        simple_messages.append({
                            'role': msg['message_role'],
                            'content': msg['message_content']
                        })
                
                print(f"📚 Loaded {len(simple_messages)} messages from DB")
                return simple_messages
                
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    async def extract_customer_context(self, conversation_id: str) -> Optional[Dict]:
        """Extract customer info from conversation messages"""
        try:
            async with self.pool.acquire() as conn:
                # Look for function results that contain customer data
                customer_msg = await conn.fetchrow("""
                    SELECT function_output_result
                    FROM chatbot_messages 
                    WHERE conversation_id = $1 
                    AND executed_function_name = 'getCustomerByPhone'
                    AND function_output_result IS NOT NULL
                    ORDER BY message_created_at DESC
                    LIMIT 1
                """, conversation_id)
                
                if customer_msg and customer_msg['function_output_result']:
                    result = json.loads(customer_msg['function_output_result'])
                    if result.get('data'):
                        print(f"👤 Found customer context in conversation")
                        return result['data']
                
                return None
                
        except Exception as e:
            print(f"❌ Error extracting customer context: {e}")
            return None
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            print("🔚 Database pool closed")

# Global instance
memory = SimpleMemory()
