"""
Simple Conversation Memory using EXISTING PostgreSQL tables
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart, TextPart

# Import asyncpg for database operations
import asyncpg
ASYNCPG_AVAILABLE = True

class SimpleMemory:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.pool = None
        self.in_memory_storage = {}  # Fallback for when no database is available
        self.use_database = bool(self.db_url)
        if self.use_database:
            # Hide password in logs
            safe_url = self.db_url.split('@')[1] if '@' in self.db_url else 'hidden'
            print(f"🔧 SimpleMemory initialized (Database: ✅ Connected to {safe_url})")
        else:
            print(f"🔧 SimpleMemory initialized (Database: ❌ No DATABASE_URL found)")
    
    async def init_pool(self):
        """Initialize database connection pool"""
        if not self.use_database:
            print("⚠️ No DATABASE_URL found - using in-memory storage")
            return
            
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=3)
                print("✅ PostgreSQL pool initialized")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                print("⚠️ Falling back to in-memory storage")
                self.use_database = False
    
    async def init_db(self):
        """Initialize database connection pool"""
        if not self.use_database:
            print("⚠️ No DATABASE_URL found - using in-memory storage")
            return
        
        if not self.db_url:
            print("⚠️ DATABASE_URL is None - using in-memory storage")
            self.use_database = False
            return
            
        if not self.pool:
            try:
                print(f"🔌 Attempting to connect to database...")
                self.pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=3)
                print("✅ PostgreSQL pool initialized successfully!")
                
                # Test the connection
                async with self.pool.acquire() as conn:
                    version = await conn.fetchval("SELECT version()")
                    print(f"🔍 PostgreSQL version: {version[:50]}...")
                    # Check if tables exist
                    tables = await conn.fetch("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('chatbot_conversations', 'chatbot_messages')
                    """)
                    print(f"📊 Found {len(tables)} chatbot tables: {[t['table_name'] for t in tables]}")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                print("⚠️ Falling back to in-memory storage")
                self.use_database = False
    
    async def get_or_create_conversation(self, user_identifier: str, platform_type: str = 'webchat') -> str:
        """Get existing conversation or create new one - MULTI-CHANNEL SUPPORT"""
        if not self.use_database:
            # In-memory fallback
            key = f"{user_identifier}_{platform_type}"
            if key not in self.in_memory_storage:
                self.in_memory_storage[key] = {
                    'conversation_id': str(uuid.uuid4()),
                    'messages': []
                }
                print(f"✅ New {platform_type} conversation created (in-memory): {self.in_memory_storage[key]['conversation_id']}")
            else:
                print(f"📚 Found existing {platform_type} conversation (in-memory): {self.in_memory_storage[key]['conversation_id']}")
            return self.in_memory_storage[key]['conversation_id']
            
        try:
            async with self.pool.acquire() as conn:
                # Get existing active conversation for this platform
                conversation = await conn.fetchrow("""
                    SELECT conversation_id FROM chatbot_conversations 
                    WHERE user_identifier = $1 AND platform_type = $2 AND is_active = true
                    ORDER BY last_message_at DESC
                    LIMIT 1
                """, user_identifier, platform_type)
                
                if conversation:
                    conv_id = str(conversation['conversation_id'])
                    print(f"📚 Found existing {platform_type} conversation: {conv_id}")
                    return conv_id
                
                # Create new conversation
                conversation_id = await conn.fetchval("""
                    INSERT INTO chatbot_conversations (user_identifier, platform_type)
                    VALUES ($1, $2)
                    RETURNING conversation_id
                """, user_identifier, platform_type)
                
                conv_id = str(conversation_id)
                print(f"✅ New {platform_type} conversation created: {conv_id}")
                return conv_id
                
        except Exception as e:
            print(f"❌ Error managing conversation: {e}")
            return str(uuid.uuid4())
    
    async def get_unified_conversation_history(self, user_identifier: str, limit: int = 20) -> List[Dict]:
        """Get conversation history across ALL channels for a user"""
        if not self.use_database:
            # In-memory fallback - get all messages for this user
            all_messages = []
            for key, data in self.in_memory_storage.items():
                if key.startswith(f"{user_identifier}_"):
                    all_messages.extend(data['messages'])
            
            # Sort by timestamp and limit
            all_messages.sort(key=lambda x: x.get('created_at', 0))
            result = all_messages[-limit:] if all_messages else []
            print(f"📚 Retrieved {len(result)} messages from in-memory storage for user: {user_identifier}")
            return result
            
        try:
            print(f"🔍 Querying database for user: {user_identifier}, limit: {limit}")
            async with self.pool.acquire() as conn:
                messages = await conn.fetch("""
                    SELECT 
                        cm.message_role as role,
                        cm.message_content as content,
                        cm.message_created_at as created_at,
                        cc.platform_type,
                        cm.executed_function_name,
                        function_input_parameters,
                        function_output_result
                    FROM chatbot_messages cm
                    JOIN chatbot_conversations cc ON cm.conversation_id = cc.conversation_id
                    WHERE cc.user_identifier = $1
                    ORDER BY cm.message_created_at DESC
                    LIMIT $2
                """, user_identifier, limit)
                
                result = [dict(msg) for msg in reversed(messages)]
                print(f"✅ Retrieved {len(result)} messages from database for user: {user_identifier}")
                if result:
                    print(f"   Latest: {result[-1].get('role')}: {result[-1].get('content', '')[:50]}...")
                return result
        except Exception as e:
            print(f"❌ Error getting unified history for user {user_identifier}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def save_user_message(self, conversation_id: str, content: str):
        """Save user message with validation (BUG-016 & BUG-017 FIX)"""
        try:
            # 🔥 BUG-016 FIX: Validate content is not empty/null
            if not content or not content.strip():
                print(f"⚠️ Skipping empty user message (BUG-016 prevention)")
                return None
            
            # 🔥 BUG-017 FIX: Truncate messages over 5000 characters
            if len(content) > 5000:
                print(f"⚠️ Truncating long user message: {len(content)} chars → 5000 chars (BUG-017 prevention)")
                content = content[:4950] + "\n\n[...message truncated for length...]"
            
            print(f"💾 Saving user message to conversation {conversation_id} (length: {len(content)} chars)")
            
            if not self.use_database:
                # In-memory fallback
                for key, data in self.in_memory_storage.items():
                    if data['conversation_id'] == conversation_id:
                        message = {
                            'role': 'user',
                            'content': content,
                            'created_at': datetime.now().isoformat()
                        }
                        data['messages'].append(message)
                        print(f"💾 User message saved (in-memory, length: {len(content)} chars)")
                        return f"in_memory_{len(data['messages'])}"
                return None
            
            async with self.pool.acquire() as conn:
                message_id = await conn.fetchval("""
                    INSERT INTO chatbot_messages (conversation_id, message_role, message_content)
                    VALUES ($1, 'user', $2)
                    RETURNING message_id
                """, conversation_id, content)
                print(f"✅ User message saved to DB (ID: {message_id}, length: {len(content)} chars)")
                return message_id
        except Exception as e:
            print(f"❌ Error saving user message: {e}")
            return None
    
    async def save_assistant_message(self, conversation_id: str, content: str, 
                                   function_name: Optional[str] = None,
                                   function_args: Optional[Dict] = None,
                                   function_result: Optional[Any] = None):
        """Save assistant message with optional function data (BUG-016 & BUG-017 FIX)"""
        try:
            # 🔥 BUG-016 FIX: Validate content is not empty/null
            if not content or not content.strip():
                print(f"⚠️ Skipping empty assistant message (BUG-016 prevention)")
                return None
            
            # 🔥 BUG-017 FIX: Truncate messages over 5000 characters
            if len(content) > 5000:
                print(f"⚠️ Truncating long assistant message: {len(content)} chars → 5000 chars (BUG-017 prevention)")
                content = content[:4950] + "\n\n[...message truncated for length...]"
            
            if not self.use_database:
                # In-memory fallback
                for key, data in self.in_memory_storage.items():
                    if data['conversation_id'] == conversation_id:
                        message = {
                            'role': 'assistant',
                            'content': content,
                            'created_at': datetime.now().isoformat(),
                            'executed_function_name': function_name,
                            'function_input_parameters': function_args,
                            'function_output_result': function_result
                        }
                        data['messages'].append(message)
                        print(f"💾 Assistant message saved (in-memory, length: {len(content)} chars)")
                        return f"in_memory_{len(data['messages'])}"
                return None
            
            async with self.pool.acquire() as conn:
                message_id = await conn.fetchval("""
                    INSERT INTO chatbot_messages (
                        conversation_id, message_role, message_content,
                        executed_function_name, function_input_parameters, function_output_result
                    ) VALUES ($1, 'assistant', $2, $3, $4, $5)
                    RETURNING message_id
                """, 
                    conversation_id, content, function_name,
                    json.dumps(function_args) if function_args else None,
                    json.dumps(function_result) if function_result else None
                )
                print(f"✅ Assistant message saved to DB (ID: {message_id}, length: {len(content)} chars)")
                return message_id
        except Exception as e:
            print(f"❌ Error saving assistant message: {e}")
            return None
    
    async def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from conversation"""
        if not self.use_database:
            # In-memory fallback
            for key, data in self.in_memory_storage.items():
                if data['conversation_id'] == conversation_id:
                    messages = data['messages'][-limit:]  # Get last N messages
                    simple_messages = []
                    for msg in messages:
                        if msg['role'] in ['user', 'assistant']:
                            simple_messages.append({
                                'role': msg['role'],
                                'content': msg['content']
                            })
                    print(f"📚 Loaded {len(simple_messages)} messages from in-memory storage")
                    return simple_messages
            return []
            
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
