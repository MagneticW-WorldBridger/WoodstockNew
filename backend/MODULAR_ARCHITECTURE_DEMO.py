"""
MODULAR ARCHITECTURE DEMO - JORGE'S PATTERN
Demonstrates 1 agent = 1 tool + orchestrator without external dependencies
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# ============================================================================
# MOCK DEPENDENCIES (NO EXTERNAL IMPORTS)
# ============================================================================

@dataclass
class MockDeps:
    """Mock dependencies for demonstration"""
    user_id: str = "demo_user"
    conversation_id: str = "demo_conv"
    loft_api_base: str = "https://api.woodstockoutlet.com/public/index.php/april"
    magento_api_base: str = "https://woodstockoutlet.com"

class MockAgent:
    """Mock agent that simulates PydanticAI behavior"""
    
    def __init__(self, model: str, instructions: str, output_type=None):
        self.model = model
        self.instructions = instructions
        self.output_type = output_type
        self.tools = []
    
    def tool(self, func):
        """Mock tool decorator"""
        self.tools.append(func)
        return func
    
    async def run(self, prompt: str, deps=None):
        """Mock run method"""
        result = await self._mock_execute(prompt, deps)
        return MockResult(result)

    async def _mock_execute(self, prompt: str, deps):
        """Mock execution logic"""
        return f"Mock response for: {prompt[:50]}..."

class MockResult:
    """Mock result wrapper"""
    def __init__(self, output):
        self.output = output

# ============================================================================
# JORGE'S PATTERN: SPECIALIZED AGENTS (1 AGENT = 1 TOOL)
# ============================================================================

class CustomerAgentDemo:
    """SPECIALIZED: Only handles customer identification"""
    
    def __init__(self):
        self.agent = MockAgent(
            'openai:gpt-4o',
            instructions="You are a CUSTOMER IDENTIFICATION SPECIALIST. Find customers by phone/email ONLY.",
            output_type=dict
        )
    
    async def search_customer(self, identifier: str, type: str = "auto"):
        """Single tool: customer search"""
        print(f"🔍 CustomerAgent: Searching for {identifier}")
        
        # Mock customer search logic
        if "404-916-2522" in identifier:
            return {
                "found": True,
                "customer_id": "9318667498",
                "name": "Daniele & Selene uriostgui",
                "email": "selenebarcia448@gmail.com",
                "phone": "404-916-2522",
                "html": """
                <div class="customer-card">
                    <h3>👤 Customer Found</h3>
                    <p><strong>Hello Daniele & Selene!</strong> Great to see you again.</p>
                    <p>📱 404-916-2522 | 🆔 ID: 9318667498 | 📧 selenebarcia448@gmail.com</p>
                </div>
                """
            }
        else:
            return {"found": False, "error": "Customer not found"}

class OrderAgentDemo:
    """SPECIALIZED: Only handles order management"""
    
    def __init__(self):
        self.agent = MockAgent(
            'openai:gpt-4o',
            instructions="You are an ORDER MANAGEMENT SPECIALIST. Handle orders ONLY.",
            output_type=dict
        )
    
    async def get_orders_by_customer(self, customer_id: str):
        """Single tool: order lookup"""
        print(f"📦 OrderAgent: Getting orders for {customer_id}")
        
        # Mock order data
        if customer_id == "9318667498":
            orders = [
                {"order_id": "ORD001", "status": "Delivered", "total": "$1,299.99", "date": "2024-01-15"},
                {"order_id": "ORD002", "status": "Processing", "total": "$899.99", "date": "2024-02-20"}
            ]
            return {
                "found": True,
                "orders": orders,
                "total_orders": len(orders),
                "html": f"""
                <div class="orders-list">
                    <h3>📦 Order History ({len(orders)} orders)</h3>
                    <div class="order-item">
                        <h4>🛍️ Order #1: ORD001</h4>
                        <p><strong>Status:</strong> Delivered | <strong>Total:</strong> $1,299.99</p>
                    </div>
                    <div class="order-item">
                        <h4>🛍️ Order #2: ORD002</h4>
                        <p><strong>Status:</strong> Processing | <strong>Total:</strong> $899.99</p>
                    </div>
                </div>
                """
            }
        return {"found": False, "error": "No orders found"}

class ProductAgentDemo:
    """SPECIALIZED: Only handles product search"""
    
    def __init__(self):
        self.agent = MockAgent(
            'openai:gpt-4o', 
            instructions="You are a PRODUCT CATALOG SPECIALIST. Search products ONLY.",
            output_type=dict
        )
    
    async def search_products(self, query: str, page_size: int = 8):
        """Single tool: product search"""
        print(f"🛒 ProductAgent: Searching '{query}'")
        
        # Mock product data
        products = [
            {"sku": "SOFA001", "name": "Grey Sectional Sofa", "price": 1299.99},
            {"sku": "SOFA002", "name": "Modern Grey Loveseat", "price": 899.99},
            {"sku": "SOFA003", "name": "Grey Fabric Recliner", "price": 599.99}
        ]
        
        return {
            "found": True,
            "products": products,
            "total_found": len(products),
            "query": query,
            "html_carousel": f"""
            CAROUSEL_DATA:
            <div class="product-carousel">
                <h3>🛒 {query.title()} - {len(products)} Found</h3>
                <div class="carousel-items">
                    {"".join([f'<div class="product-card"><h4>{p["name"]}</h4><p>${p["price"]}</p></div>' for p in products])}
                </div>
            </div>
            """
        }

# ============================================================================
# JORGE'S PATTERN: ORCHESTRATOR (NO TOOLS - ONLY ROUTING)
# ============================================================================

class OrchestratorDemo:
    """MAIN ORCHESTRATOR: NO TOOLS - Only routes to specialists"""
    
    def __init__(self):
        self.agent = MockAgent(
            'openai:gpt-4o',
            instructions="""
            You are the MAIN ORCHESTRATOR for Woodstock AI.
            You have NO TOOLS. Your job is to ROUTE requests to specialists:
            - customer_agent: Customer lookup
            - order_agent: Order management  
            - product_agent: Product search
            NEVER try to do the work yourself. ALWAYS delegate.
            """
        )
        
        # Initialize specialist agents
        self.customer_agent = CustomerAgentDemo()
        self.order_agent = OrderAgentDemo()
        self.product_agent = ProductAgentDemo()
    
    async def route_request(self, user_message: str) -> str:
        """Route request to appropriate specialist"""
        
        print(f"🎯 Orchestrator: Routing '{user_message}'")
        
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["phone", "customer", "404-916-2522"]):
            # Route to customer agent
            identifier = self._extract_identifier(user_message)
            result = await self.customer_agent.search_customer(identifier)
            return f"CUSTOMER_RESULT: {json.dumps(result)}"
        
        elif any(word in message_lower for word in ["orders", "order history", "my orders"]):
            # Route to order agent (needs customer_id)
            customer_id = "9318667498"  # Mock extraction
            result = await self.order_agent.get_orders_by_customer(customer_id)
            return f"ORDER_RESULT: {json.dumps(result)}"
        
        elif any(word in message_lower for word in ["sofa", "sectional", "furniture", "search"]):
            # Route to product agent
            result = await self.product_agent.search_products(user_message)
            return f"PRODUCT_RESULT: {json.dumps(result)}"
        
        else:
            return "ERROR: Unable to route request. Please specify customer, order, or product query."
    
    def _extract_identifier(self, message: str) -> str:
        """Extract phone/email from message"""
        if "404-916-2522" in message:
            return "404-916-2522"
        return "unknown"

# ============================================================================
# JORGE'S PATTERN: CHAIN EXECUTOR (ASYNC MULTI-STEP)
# ============================================================================

class ChainExecutorDemo:
    """Executes chained commands asynchronously"""
    
    def __init__(self, orchestrator: OrchestratorDemo):
        self.orchestrator = orchestrator
    
    async def execute_customer_order_chain(self, identifier: str) -> Dict[str, Any]:
        """
        Execute Jorge's main use case: phone → customer → orders → details → HTML
        """
        
        print(f"🔗 Starting customer order chain for {identifier}")
        
        chain_results = []
        
        try:
            # Step 1: Find customer
            print("🔗 Step 1: Finding customer...")
            customer_result = await self.orchestrator.customer_agent.search_customer(identifier)
            chain_results.append({"step": "customer", "result": customer_result})
            
            if not customer_result.get("found"):
                return {"success": False, "error": "Customer not found", "results": chain_results}
            
            # Step 2: Get orders
            print("🔗 Step 2: Getting orders...")
            customer_id = customer_result["customer_id"]
            order_result = await self.orchestrator.order_agent.get_orders_by_customer(customer_id)
            chain_results.append({"step": "orders", "result": order_result})
            
            # Step 3: Generate combined HTML
            print("🔗 Step 3: Generating combined HTML...")
            final_html = self._combine_results(customer_result, order_result)
            
            return {
                "success": True,
                "steps_completed": 3,
                "final_output": final_html,
                "results": chain_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": chain_results
            }
    
    def _combine_results(self, customer_result: dict, order_result: dict) -> str:
        """Combine results into beautiful HTML"""
        
        html = f"""
        <div class="customer-journey">
            <h2>🎯 Complete Customer Journey</h2>
            {customer_result.get('html', '')}
            {order_result.get('html', '')}
            <div class="journey-summary">
                <p><strong>✅ Journey Complete:</strong> Found customer and {order_result.get('total_orders', 0)} orders</p>
            </div>
        </div>
        """
        return html

# ============================================================================
# DEMO RUNNER
# ============================================================================

async def demo_jorge_architecture():
    """Demonstrate Jorge's modular architecture"""
    
    print("🚀 JORGE'S MODULAR ARCHITECTURE DEMO")
    print("=" * 60)
    print("Pattern: 1 agent = 1 tool + orchestrator")
    print()
    
    # Initialize system
    orchestrator = OrchestratorDemo()
    chain_executor = ChainExecutorDemo(orchestrator)
    
    # Test 1: Individual agent specialization
    print("📋 TEST 1: Agent Specialization")
    print("-" * 30)
    
    print("🔍 Customer Agent (ONLY customer lookup):")
    customer_result = await orchestrator.customer_agent.search_customer("404-916-2522")
    print(f"   Result: {customer_result['found']} - {customer_result.get('name', 'N/A')}")
    
    print("📦 Order Agent (ONLY order management):")
    order_result = await orchestrator.order_agent.get_orders_by_customer("9318667498")
    print(f"   Result: {order_result['found']} - {order_result.get('total_orders', 0)} orders")
    
    print("🛒 Product Agent (ONLY product search):")
    product_result = await orchestrator.product_agent.search_products("grey sofas")
    print(f"   Result: {product_result['found']} - {product_result.get('total_found', 0)} products")
    
    # Test 2: Orchestrator routing (NO TOOLS)
    print("\n📋 TEST 2: Orchestrator Routing (NO TOOLS)")
    print("-" * 40)
    
    test_messages = [
        "Find customer with phone 404-916-2522",
        "Show my orders", 
        "Search grey sofas"
    ]
    
    for msg in test_messages:
        result = await orchestrator.route_request(msg)
        print(f"   '{msg}' → {result[:80]}...")
    
    # Test 3: Chained command (Jorge's main use case)
    print("\n📋 TEST 3: Chained Command Execution")
    print("-" * 35)
    
    chain_result = await chain_executor.execute_customer_order_chain("404-916-2522")
    print(f"   Chain Success: {chain_result['success']}")
    print(f"   Steps Completed: {chain_result.get('steps_completed', 0)}")
    print(f"   Final Output: {len(chain_result.get('final_output', ''))} characters of HTML")
    
    # Test 4: Async parallel execution
    print("\n📋 TEST 4: Async Parallel Execution")
    print("-" * 33)
    
    import time
    start_time = time.time()
    
    # Run multiple operations in parallel (Jorge's async recommendation)
    tasks = [
        orchestrator.customer_agent.search_customer("404-916-2522"),
        orchestrator.product_agent.search_products("sectionals"),
        orchestrator.product_agent.search_products("recliners")
    ]
    
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"   Parallel execution: {end_time - start_time:.3f} seconds")
    print(f"   Operations completed: {len(results)}")
    print(f"   All successful: {all(r.get('found', False) for r in results)}")
    
    print("\n✅ DEMO COMPLETE!")
    print("🎯 Jorge's pattern successfully demonstrated:")
    print("   ✅ 1 agent = 1 tool (specialization)")
    print("   ✅ Orchestrator with NO tools (routing only)")  
    print("   ✅ Async chain execution (multi-step workflows)")
    print("   ✅ Parallel execution (non-blocking)")

if __name__ == "__main__":
    print("🧪 Woodstock Modular Architecture Demo")
    print("Following Jorge G's recommendations\n")
    
    # Run the demo
    asyncio.run(demo_jorge_architecture())
