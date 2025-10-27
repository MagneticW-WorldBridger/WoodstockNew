#!/usr/bin/env python3
"""
Working Memory Backend - Uses your existing database
"""

import json
import asyncio
import re
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import FastAPI
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, HTMLResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    print("⚠️ FastAPI not available - installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'fastapi', 'uvicorn', 'pydantic'])
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, HTMLResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True

# Try to import asyncpg
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    print("⚠️ asyncpg not available - installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'asyncpg'])
    import asyncpg
    ASYNCPG_AVAILABLE = True

class WorkingMemory:
    """Working memory system using your PostgreSQL database"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.pool = None
        print(f"🔧 WorkingMemory initialized (Database: {'✅' if self.db_url else '❌'})")
    
    async def init_db(self):
        """Initialize database connection"""
        if not self.db_url:
            print("❌ No DATABASE_URL found!")
            return False
            
        try:
            self.pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=3)
            print("✅ PostgreSQL pool initialized")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def get_or_create_conversation(self, user_identifier: str, platform_type: str = 'webchat') -> str:
        """Get existing conversation or create new one"""
        try:
            async with self.pool.acquire() as conn:
                # Get existing active conversation
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
    
    async def save_user_message(self, conversation_id: str, content: str):
        """Save user message"""
        try:
            async with self.pool.acquire() as conn:
                message_id = await conn.fetchval("""
                    INSERT INTO chatbot_messages (conversation_id, message_role, message_content)
                    VALUES ($1, 'user', $2)
                    RETURNING message_id
                """, conversation_id, content)
                print(f"💾 User message saved: {content[:50]}...")
                return message_id
        except Exception as e:
            print(f"❌ Error saving user message: {e}")
            return None
    
    async def save_assistant_message(self, conversation_id: str, content: str):
        """Save assistant message"""
        try:
            async with self.pool.acquire() as conn:
                message_id = await conn.fetchval("""
                    INSERT INTO chatbot_messages (conversation_id, message_role, message_content)
                    VALUES ($1, 'assistant', $2)
                    RETURNING message_id
                """, conversation_id, content)
                print(f"💾 Assistant message saved: {content[:50]}...")
                return message_id
        except Exception as e:
            print(f"❌ Error saving assistant message: {e}")
            return None
    
    async def get_recent_messages(self, conversation_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from conversation"""
        try:
            async with self.pool.acquire() as conn:
                messages = await conn.fetch("""
                    SELECT message_role, message_content
                    FROM chatbot_messages 
                    WHERE conversation_id = $1
                    ORDER BY message_created_at ASC
                    LIMIT $2
                """, conversation_id, limit)
                
                simple_messages = []
                for msg in messages:
                    simple_messages.append({
                        'role': msg['message_role'],
                        'content': msg['message_content']
                    })
                
                print(f"📚 Loaded {len(simple_messages)} messages from database")
                return simple_messages
                
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    async def get_unified_conversation_history(self, user_identifier: str, limit: int = 20) -> List[Dict]:
        """Get conversation history for a user"""
        try:
            async with self.pool.acquire() as conn:
                messages = await conn.fetch("""
                    SELECT 
                        cm.message_role as role,
                        cm.message_content as content,
                        cm.message_created_at as created_at
                    FROM chatbot_messages cm
                    JOIN chatbot_conversations cc ON cm.conversation_id = cc.conversation_id
                    WHERE cc.user_identifier = $1
                    ORDER BY cm.message_created_at DESC
                    LIMIT $2
                """, user_identifier, limit)
                
                return [dict(msg) for msg in reversed(messages)]
        except Exception as e:
            print(f"❌ Error getting unified history: {e}")
            return []
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            print("🔚 Database pool closed")

# Initialize memory
memory = WorkingMemory()

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    user_identifier: Optional[str] = None
    platform_type: Optional[str] = 'webchat'

class ChatResponse(BaseModel):
    choices: List[dict]
    model: str
    usage: dict

# Initialize FastAPI app
app = FastAPI(
    title="LOFT Chat Backend with Working Memory",
    description="Smart chat backend with PostgreSQL memory",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_user_identifier(message: str) -> str:
    """Extract phone or email from message"""
    # Phone pattern
    phone_match = re.search(r'\b\d{3}-\d{3}-\d{4}\b', message)
    if phone_match:
        return phone_match.group()
    
    # Email pattern
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
    if email_match:
        return email_match.group()
    
    return f"webchat_user_{hash(message) % 10000}"

def should_use_memory(message: str, user_identifier: str) -> bool:
    """Determine if we should use memory or start fresh"""
    message_lower = message.lower()
    
    # Force new session triggers
    new_session_triggers = [
        'new chat', 'start over', 'clear history', 'reset', 'begin again',
        'different customer', 'another customer', 'switch customer'
    ]
    
    if any(trigger in message_lower for trigger in new_session_triggers):
        print(f"🆕 NEW SESSION triggered by: {message}")
        return False
    
    # Use memory triggers  
    memory_triggers = [
        'my orders', 'her orders', 'his orders', 'their orders',
        'that order', 'this order', 'the order', 'those orders',
        'show me', 'get details', 'more info', 'tell me more',
        'what about', 'details on', 'expand on', 'continue',
        'picture', 'image', 'photo', 'show', 'display'
    ]
    
    if any(trigger in message_lower for trigger in memory_triggers):
        print(f"🧠 MEMORY triggered by: {message}")
        return True
    
    # If user identifier found and it's a direct lookup, use memory  
    if user_identifier and (user_identifier in message):
        print(f"👤 MEMORY for known user: {user_identifier}")
        return True
    
    # Default: use memory for continuity
    return True

async def generate_ai_response(user_message: str, message_history: list) -> str:
    """Generate AI response based on user message and history"""
    
    # Check if this is a follow-up question that needs context
    message_lower = user_message.lower()
    
    # If asking about "picture", "image", "show me", etc. and we have history
    if any(term in message_lower for term in ['picture', 'image', 'photo', 'show me', 'display']) and message_history:
        # Look for product-related context in history
        for msg in reversed(message_history):
            if 'product' in msg['content'].lower() or 'sectional' in msg['content'].lower() or 'furniture' in msg['content'].lower():
                return f"I remember you were asking about products! Based on our conversation, here are the product images you requested. [This would show the actual product images from the previous context]"
    
    # If asking about orders and we have customer context
    if any(term in message_lower for term in ['orders', 'order', 'purchase', 'bought']) and message_history:
        for msg in reversed(message_history):
            if 'customer' in msg['content'].lower() or 'phone' in msg['content'].lower() or 'email' in msg['content'].lower():
                return f"I remember you! Let me look up your order information. [This would call the LOFT API with your customer details]"
    
    # Default response
    return f"I understand you're asking about: {user_message}. How can I help you with furniture and home furnishings today?"

# Main chat completions endpoint with MEMORY
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """Chat completions with conversation memory"""
    try:
        print(f"📨 Chat request received: {len(request.messages)} messages")
        
        # Extract user message
        user_message = request.messages[-1].content if request.messages else ""
        print(f"🤖 Processing prompt: {user_message[:50]}...")
        
        # Extract user identifier from message or use session info
        user_identifier = None
        if request.user_identifier:
            user_identifier = request.user_identifier
        else:
            user_identifier = extract_user_identifier(user_message)
        
        print(f"👤 User identifier: {user_identifier}")
        
        # SMART SESSION MANAGEMENT
        use_memory = should_use_memory(user_message, user_identifier)
        print(f"🧠 Memory decision: {'USE MEMORY' if use_memory else 'NEW SESSION'}")
        
        # Get platform type
        platform_type = request.platform_type if request.platform_type else 'webchat'
        
        # Get or create conversation
        if use_memory:
            conversation_id = await memory.get_or_create_conversation(user_identifier, platform_type)
        else:
            # Force new conversation for fresh start
            conversation_id = await memory.get_or_create_conversation(f"{user_identifier}_new_{int(asyncio.get_event_loop().time())}", platform_type)
            print(f"🆕 Starting NEW {platform_type} session for: {user_identifier}")
        
        # Get conversation history
        db_messages = await memory.get_unified_conversation_history(user_identifier, limit=10)
        
        print(f"📚 Using {len(db_messages)} historical messages")
        
        # Generate AI response with context
        ai_response = await generate_ai_response(user_message, db_messages)
        
        # Save user message
        await memory.save_user_message(conversation_id, user_message)
        
        # Save assistant response
        await memory.save_assistant_message(conversation_id, ai_response)
        
        # Return response
        response = ChatResponse(
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": ai_response
                },
                "finish_reason": "stop"
            }],
            model="loft-chat",
            usage={
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(ai_response.split()),
                "total_tokens": len(user_message.split()) + len(ai_response.split())
            }
        )
        return response
    
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "LOFT Chat Backend with Working Memory is running!",
        "memory": "PostgreSQL Database",
        "features": ["Conversation Memory", "Context Awareness", "User Identification"]
    }

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LOFT Chat Backend v2.0 - WITH WORKING MEMORY!</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }
            .container { max-width: 800px; margin: auto; background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            h1 { text-align: center; font-size: 2.5em; margin-bottom: 10px; }
            .status { text-align: center; font-size: 1.3em; color: #FFD700; margin-bottom: 30px; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
            .feature { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.2); }
            .feature h3 { color: #FFD700; margin-bottom: 10px; }
            code { background: rgba(0, 0, 0, 0.3); padding: 4px 8px; border-radius: 4px; }
            a { color: #FFD700; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 LOFT Chat Backend v2.0</h1>
            <div class="status">
                ✅ NOW WITH WORKING POSTGRESQL MEMORY! ✅
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🔧 Backend Features</h3>
                    <ul>
                        <li>✅ FastAPI + PostgreSQL</li>
                        <li>✅ Database Memory</li>
                        <li>✅ Conversation History</li>
                        <li>✅ Context Preservation</li>
                        <li>✅ User Identification</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>🎯 Memory Features</h3>
                    <ul>
                        <li>📱 Remembers user context</li>
                        <li>📦 Tracks conversation flow</li>
                        <li>🛍️ Maintains product context</li>
                        <li>🧠 Context awareness</li>
                        <li>🤖 Smart session management</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>🚀 Test Memory</h3>
                    <p><strong>Example conversation:</strong></p>
                    <ol>
                        <li>Say: <code>I want to see sectionals</code></li>
                        <li>Then: <code>Show me the picture</code></li>
                        <li>AI remembers you were asking about sectionals! 🎉</li>
                    </ol>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px; font-size: 1.2em;">
                <p>💡 <strong>The AI now remembers your conversation!</strong></p>
                <p>✨ Uses PostgreSQL database for persistent storage ✨</p>
            </div>
        </div>
    </body>
    </html>
    """

# Startup and shutdown events
async def startup_event():
    """Initialize services on startup"""
    success = await memory.init_db()
    if not success:
        print("❌ Failed to initialize database - memory will not work properly")

async def shutdown_event():
    """Clean up on shutdown"""
    await memory.close()

# Register lifespan events
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8001))
    print("🚀 Starting LOFT Chat Backend with WORKING MEMORY...")
    print(f"🧠 Memory: PostgreSQL Database")
    print(f"🌐 Web UI: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
