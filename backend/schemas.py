"""Simple Pydantic Models for LOFT Chat"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    """Chat request model"""
    messages: List[ChatMessage] = Field(..., description="Chat history")
    stream: bool = Field(default=True, description="Enable streaming")
    model: Optional[str] = Field(default="loft-chat", description="Model to use")
    temperature: Optional[float] = Field(default=0.7, description="Response temperature")
    
    # Session management for conversation memory
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation tracking")
    user_identifier: Optional[str] = Field(default=None, description="User identifier (phone, email, etc.)")
    platform_type: Optional[str] = Field(default="webchat", description="Platform: webchat, phone, sms, facebook, instagram")
    channel_metadata: Optional[Dict] = Field(default=None, description="Channel-specific metadata (call_id, phone_number, etc.)")
    
    # 🔐 URL PARAMETER AUTHENTICATION - NEW!
    customer_id: Optional[str] = Field(default=None, description="Customer ID from URL parameters (authenticated user)")
    loft_id: Optional[str] = Field(default=None, description="LOFT customer ID from URL parameters")
    email: Optional[str] = Field(default=None, description="Customer email from URL parameters (authenticated user)")
    auth_level: Optional[str] = Field(default="anonymous", description="Authentication level: anonymous, authenticated, admin")

class ChatResponse(BaseModel):
    """Chat response model"""
    choices: List[Dict[str, Any]] = Field(..., description="Response choices")
    model: str = Field(..., description="Model used")
    usage: Optional[Dict[str, int]] = None
