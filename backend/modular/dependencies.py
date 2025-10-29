"""
SHARED DEPENDENCIES FOR MODULAR AGENT ARCHITECTURE
Following Context7 + Jorge's recommendations
"""

import os
import httpx
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

# ============================================================================
# SHARED DEPENDENCIES (INJECTED INTO ALL AGENTS)
# ============================================================================

@dataclass
class SharedDeps:
    """Dependency injection for all agents - Context7 pattern"""
    
    # API Clients (shared across all agents)
    http_client: httpx.AsyncClient
    
    # API Configuration
    loft_api_base: str
    magento_api_base: str
    magento_token: Optional[str] = None
    
    # Context Management (shared state)
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    
    # Database connections would go here
    # db_pool: Optional[Any] = None

    @classmethod
    async def create(cls, user_id: str = None, conversation_id: str = None):
        """Factory method to create shared dependencies"""
        return cls(
            http_client=httpx.AsyncClient(timeout=15.0),
            loft_api_base=os.getenv('WOODSTOCK_API_BASE', 'https://api.woodstockoutlet.com/public/index.php/april'),
            magento_api_base='https://woodstockoutlet.com',
            magento_token=os.getenv('MAGENTO_ADMIN_TOKEN'),
            user_id=user_id,
            conversation_id=conversation_id
        )
    
    async def cleanup(self):
        """Clean up resources"""
        await self.http_client.aclose()

# ============================================================================
# STRUCTURED OUTPUT MODELS (PYDANTIC FOR TYPE SAFETY)
# ============================================================================

class CustomerResult(BaseModel):
    """Structured customer data"""
    found: bool
    customer_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    html: Optional[str] = None  # Formatted HTML for display
    
class OrderResult(BaseModel):
    """Structured order data"""
    found: bool
    orders: List[Dict[str, Any]] = []
    customer_id: Optional[str] = None
    total_orders: int = 0
    html: Optional[str] = None  # Formatted HTML for display

class ProductResult(BaseModel):
    """Structured product search results"""
    found: bool
    products: List[Dict[str, Any]] = []
    total_found: int = 0
    query: str = ""
    html_carousel: Optional[str] = None  # CAROUSEL_DATA for frontend
    suggested_filters: List[str] = []

class ChainResult(BaseModel):
    """Result of a chained command execution"""
    success: bool
    steps_completed: int
    total_steps: int
    final_output: Optional[str] = None
    error: Optional[str] = None
    intermediate_results: List[Dict[str, Any]] = []

# ============================================================================
# CHAIN EXECUTION MODELS
# ============================================================================

class ChainStep(BaseModel):
    """Single step in a chained command"""
    step_id: str
    agent_name: str
    tool_name: str
    params: Dict[str, Any]
    depends_on: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    completed: bool = False
    
class ChainCommand(BaseModel):
    """Complete chained command definition"""
    chain_id: str
    user_goal: str  # Original user request
    steps: List[ChainStep]
    current_step: int = 0
    created_at: datetime = datetime.now()
