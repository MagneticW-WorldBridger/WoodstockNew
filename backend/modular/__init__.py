"""
MODULAR AGENT ARCHITECTURE FOR WOODSTOCK AI
Following Jorge's recommendations: 1 agent = 1 tool + orchestrator
"""

from .dependencies import SharedDeps, CustomerResult, OrderResult, ProductResult, ChainResult
from .customer_agent import customer_agent
from .order_agent import order_agent
from .product_agent import product_agent
from .orchestrator import orchestrator_agent, chain_executor

__version__ = "1.0.0"
__architecture__ = "jorge_modular_pattern"

# Export main components
__all__ = [
    "SharedDeps",
    "CustomerResult", 
    "OrderResult",
    "ProductResult",
    "ChainResult",
    "customer_agent",
    "order_agent", 
    "product_agent",
    "orchestrator_agent",
    "chain_executor"
]
