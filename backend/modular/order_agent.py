"""
ORDER AGENT - 1 AGENT = 1 TOOL (Jorge's Pattern)
Handles ONLY order management and history
"""

from pydantic_ai import Agent, RunContext
from .dependencies import SharedDeps, OrderResult
import json

# ============================================================================
# ORDER SPECIALIZED AGENT
# ============================================================================

order_agent = Agent[SharedDeps, OrderResult](
    'openai:gpt-4o',
    deps_type=SharedDeps,
    output_type=OrderResult,
    instructions="""
    You are an ORDER MANAGEMENT SPECIALIST.
    Your ONLY job is to handle order lookups and details using LOFT API.
    
    RULES:
    1. Use order_operations tool for ALL order-related tasks
    2. Return OrderResult with structured data + HTML
    3. NEVER search customers or products - that's other agents' jobs
    4. Format order data beautifully for customer display
    """
)

@order_agent.tool
async def order_operations(ctx: RunContext[SharedDeps], operation: str, **params) -> OrderResult:
    """
    Handle order operations: list orders, get details, track status
    
    Args:
        operation: "list_by_customer", "get_details", "track_status"
        params: Operation-specific parameters
    """
    
    print(f"🔧 OrderAgent: {operation} with params {params}")
    
    try:
        if operation == "list_by_customer":
            return await _get_orders_by_customer(ctx, params.get('customer_id'))
        elif operation == "get_details":
            return await _get_order_details(ctx, params.get('order_id'))
        else:
            return OrderResult(
                found=False,
                html=f"<div class='error'>Unknown operation: {operation}</div>"
            )
            
    except Exception as e:
        print(f"❌ OrderAgent error: {e}")
        return OrderResult(
            found=False,
            html=f"<div class='error'>Order operation failed: {str(e)}</div>"
        )

async def _get_orders_by_customer(ctx: RunContext[SharedDeps], customer_id: str) -> OrderResult:
    """Get all orders for a customer"""
    
    url = f"{ctx.deps.loft_api_base}/GetOrdersByCustomer"
    params = {'custid': customer_id}
    
    print(f"🌐 OrderAgent: Getting orders for customer {customer_id}")
    response = await ctx.deps.http_client.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    if data and data.get('entry') and len(data['entry']) > 0:
        orders = data['entry']
        
        # Generate HTML for order list
        html_orders = []
        for i, order in enumerate(orders[:5], 1):  # Show top 5
            html_orders.append(f"""
            <div class="order-item">
                <h4>🛍️ Order #{i}</h4>
                <p><strong>Order ID:</strong> {order.get('orderid', 'N/A')}</p>
                <p><strong>Status:</strong> {order.get('orderstatus', 'N/A')}</p>
                <p><strong>Total:</strong> ${order.get('ordertotal', '0')}</p>
                <p><strong>Date:</strong> {order.get('orderdate', 'N/A')}</p>
            </div>
            """)
        
        html = f"""
        <div class="orders-list">
            <h3>📦 Order History ({len(orders)} orders)</h3>
            {''.join(html_orders)}
            {f'<p>...and {len(orders) - 5} more orders</p>' if len(orders) > 5 else ''}
        </div>
        """
        
        return OrderResult(
            found=True,
            orders=orders,
            customer_id=customer_id,
            total_orders=len(orders),
            html=html
        )
    else:
        return OrderResult(
            found=False,
            customer_id=customer_id,
            html="<div class='info'>No orders found for this customer</div>"
        )

async def _get_order_details(ctx: RunContext[SharedDeps], order_id: str) -> OrderResult:
    """Get detailed order information"""
    
    url = f"{ctx.deps.loft_api_base}/GetDetailsByOrder"
    params = {'orderid': order_id}
    
    print(f"🌐 OrderAgent: Getting details for order {order_id}")
    response = await ctx.deps.http_client.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    if data and data.get('entry'):
        order_details = data['entry']
        
        # Generate detailed HTML
        html = f"""
        <div class="order-details">
            <h3>📦 Order Details #{order_id}</h3>
            <div class="order-items">
        """
        
        for item in order_details:
            html += f"""
            <div class="order-item-detail">
                <h4>{item.get('product_name', 'Product')}</h4>
                <p><strong>SKU:</strong> {item.get('product_sku', 'N/A')}</p>
                <p><strong>Quantity:</strong> {item.get('qty', 1)}</p>
                <p><strong>Price:</strong> ${item.get('price', '0')}</p>
            </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return OrderResult(
            found=True,
            orders=[{"order_id": order_id, "details": order_details}],
            html=html
        )
    else:
        return OrderResult(
            found=False,
            html=f"<div class='error'>Order {order_id} not found</div>"
        )
