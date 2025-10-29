"""
MODULAR MAIN SYSTEM - JORGE'S ARCHITECTURE
Replaces monolithic main.py with specialized agents + orchestrator
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import asyncio

# Import our modular system
from .dependencies import SharedDeps
from .orchestrator import orchestrator_agent, chain_executor
from .customer_agent import customer_agent
from .order_agent import order_agent
from .product_agent import product_agent

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Woodstock AI - Modular Architecture",
    description="Jorge's 1 agent = 1 tool pattern with orchestrator",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ModularChatRequest(BaseModel):
    messages: list[Dict[str, str]]
    stream: bool = True
    # Auth params
    customer_id: Optional[str] = None
    email: Optional[str] = None
    loft_id: Optional[str] = None
    auth_level: str = "anonymous"

class ModularChatResponse(BaseModel):
    choices: list[Dict[str, Any]]
    model: str = "modular-woodstock"

# ============================================================================
# MAIN CHAT ENDPOINT (MODULAR)
# ============================================================================

@app.post("/v1/chat/completions")
async def modular_chat_completions(request: ModularChatRequest):
    """
    Main chat endpoint using Jorge's modular architecture
    Routes requests through orchestrator to specialized agents
    """
    
    print(f"🚀 Modular chat request: {len(request.messages)} messages")
    
    # Get the latest user message
    user_message = ""
    for msg in reversed(request.messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    if not user_message:
        raise HTTPException(400, "No user message found")
    
    # Create shared dependencies for this request
    deps = await SharedDeps.create(
        user_id=request.customer_id or "anonymous", 
        conversation_id=f"conv_{hash(str(request.messages))}"
    )
    
    try:
        # Route based on user intent (orchestrator decides)
        if await _is_chained_request(user_message):
            # Handle multi-step chained commands
            return await _handle_chained_request(user_message, deps, request.stream)
        else:
            # Handle single-step requests via orchestrator
            return await _handle_single_request(user_message, deps, request.stream)
    
    finally:
        # Cleanup shared resources
        await deps.cleanup()

async def _is_chained_request(user_message: str) -> bool:
    """Detect if this requires a multi-step chain"""
    
    chain_triggers = [
        "tell me everything about customer",
        "complete customer journey", 
        "customer info and orders",
        "full customer profile"
    ]
    
    return any(trigger in user_message.lower() for trigger in chain_triggers)

async def _handle_chained_request(user_message: str, deps: SharedDeps, stream: bool):
    """Handle multi-step chained commands"""
    
    print(f"🔗 Processing chained request: {user_message}")
    
    # Extract identifier from message (phone/email)
    identifier = _extract_identifier(user_message)
    if not identifier:
        return _error_response("Please provide a phone number or email for customer lookup")
    
    # Execute the chain asynchronously 
    chain_result = await chain_executor.execute_customer_order_chain(deps, identifier)
    
    if stream:
        return StreamingResponse(
            _stream_chain_result(chain_result),
            media_type="text/plain"
        )
    else:
        return ModularChatResponse(
            choices=[{
                "message": {
                    "role": "assistant",
                    "content": chain_result.final_output or chain_result.error or "Chain completed"
                }
            }]
        )

async def _handle_single_request(user_message: str, deps: SharedDeps, stream: bool):
    """Handle single requests via orchestrator routing"""
    
    print(f"🎯 Processing single request via orchestrator: {user_message}")
    
    # Let orchestrator decide how to route this
    result = await orchestrator_agent.run(user_message, deps=deps)
    response_content = result.output
    
    if stream:
        return StreamingResponse(
            _stream_single_response(response_content),
            media_type="text/plain"
        )
    else:
        return ModularChatResponse(
            choices=[{
                "message": {
                    "role": "assistant", 
                    "content": response_content
                }
            }]
        )

# ============================================================================
# STREAMING HELPERS
# ============================================================================

async def _stream_chain_result(chain_result):
    """Stream chained command results"""
    
    # Stream progress updates
    yield f'data: {{"choices": [{{"delta": {{"content": "🔗 Executing customer journey...\\n"}}}}], "model": "modular-woodstock"}}\n\n'
    
    await asyncio.sleep(0.1)
    
    # Stream each step completion
    for i in range(chain_result.steps_completed):
        yield f'data: {{"choices": [{{"delta": {{"content": "✅ Step {i+1} completed\\n"}}}}], "model": "modular-woodstock"}}\n\n'
        await asyncio.sleep(0.2)
    
    # Stream final result
    if chain_result.success and chain_result.final_output:
        # Split into chunks for streaming
        content = chain_result.final_output
        chunk_size = 50
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            yield f'data: {{"choices": [{{"delta": {{"content": "{chunk}"}}}}], "model": "modular-woodstock"}}\n\n'
            await asyncio.sleep(0.1)
    else:
        error_msg = chain_result.error or "Chain execution failed"
        yield f'data: {{"choices": [{{"delta": {{"content": "{error_msg}"}}}}], "model": "modular-woodstock"}}\n\n'
    
    # End stream
    yield "data: [DONE]\n\n"

async def _stream_single_response(content: str):
    """Stream single response content"""
    
    chunk_size = 30
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i+chunk_size]
        yield f'data: {{"choices": [{{"delta": {{"content": "{chunk}"}}}}], "model": "modular-woodstock"}}\n\n'
        await asyncio.sleep(0.1)
    
    yield "data: [DONE]\n\n"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _extract_identifier(message: str) -> Optional[str]:
    """Extract phone number or email from message"""
    
    import re
    
    # Look for email pattern
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
    if email_match:
        return email_match.group()
    
    # Look for phone pattern
    phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', message)
    if phone_match:
        return phone_match.group()
    
    return None

def _error_response(message: str):
    """Generate error response"""
    return ModularChatResponse(
        choices=[{
            "message": {
                "role": "assistant",
                "content": f"❌ {message}"
            }
        }]
    )

# ============================================================================
# HEALTH CHECK & STATUS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check for modular system"""
    return {
        "status": "healthy",
        "architecture": "modular",
        "agents": {
            "orchestrator": "active",
            "customer_agent": "active", 
            "order_agent": "active",
            "product_agent": "active"
        },
        "pattern": "jorge_1_agent_1_tool"
    }

@app.get("/")
async def root():
    """Root endpoint info"""
    return {
        "message": "Woodstock AI - Modular Architecture",
        "architecture": "Jorge's 1 agent = 1 tool pattern",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Different port than monolithic
