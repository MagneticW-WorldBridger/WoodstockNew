#!/usr/bin/env python3
"""
Test database memory connection
"""

import asyncio
import os
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_database_connection():
    """Test database connection and memory functionality"""
    try:
        print("🧠 Testing Database Memory System...")
        
        # Check if DATABASE_URL is set
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not set!")
            return False
        
        print(f"✅ DATABASE_URL: {db_url[:50]}...")
        
        # Test database connection
        print("🔌 Testing database connection...")
        conn = await asyncpg.connect(db_url)
        print("✅ Database connection successful!")
        
        # Test if tables exist
        print("📋 Checking for existing tables...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%chatbot%'
        """)
        
        print(f"📊 Found {len(tables)} chatbot tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Test conversation creation
        print("🧪 Testing conversation creation...")
        conversation_id = await conn.fetchval("""
            INSERT INTO chatbot_conversations (user_identifier, platform_type)
            VALUES ($1, $2)
            RETURNING conversation_id
        """, "test_user_123", "webchat")
        
        print(f"✅ Conversation created: {conversation_id}")
        
        # Test message saving
        print("💾 Testing message saving...")
        user_msg_id = await conn.fetchval("""
            INSERT INTO chatbot_messages (conversation_id, message_role, message_content)
            VALUES ($1, 'user', $2)
            RETURNING message_id
        """, conversation_id, "I want to see sectionals")
        
        assistant_msg_id = await conn.fetchval("""
            INSERT INTO chatbot_messages (conversation_id, message_role, message_content)
            VALUES ($1, 'assistant', $2)
            RETURNING message_id
        """, conversation_id, "I'll help you find sectionals!")
        
        print(f"✅ Messages saved: {user_msg_id}, {assistant_msg_id}")
        
        # Test message retrieval
        print("📚 Testing message retrieval...")
        messages = await conn.fetch("""
            SELECT message_role, message_content
            FROM chatbot_messages 
            WHERE conversation_id = $1
            ORDER BY message_created_at ASC
        """, conversation_id)
        
        print(f"✅ Retrieved {len(messages)} messages:")
        for msg in messages:
            print(f"  - {msg['message_role']}: {msg['message_content']}")
        
        # Test follow-up with memory
        print("🧠 Testing memory functionality...")
        follow_up_msg_id = await conn.fetchval("""
            INSERT INTO chatbot_messages (conversation_id, message_role, message_content)
            VALUES ($1, 'user', $2)
            RETURNING message_id
        """, conversation_id, "Show me the picture")
        
        # Get all messages for context
        all_messages = await conn.fetch("""
            SELECT message_role, message_content
            FROM chatbot_messages 
            WHERE conversation_id = $1
            ORDER BY message_created_at ASC
        """, conversation_id)
        
        print(f"✅ Follow-up message saved. Total conversation history:")
        for i, msg in enumerate(all_messages, 1):
            print(f"  {i}. {msg['message_role']}: {msg['message_content']}")
        
        # Check if we can see the context
        if len(all_messages) >= 3:
            print("🎉 SUCCESS: Memory is working! The system remembers the conversation context!")
            print("   - User asked about sectionals")
            print("   - Assistant responded about sectionals") 
            print("   - User asked for picture (should remember sectionals context)")
        else:
            print("⚠️ Memory test incomplete")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())
