"""
CUSTOMER AGENT - 1 AGENT = 1 TOOL (Jorge's Pattern)
Handles ONLY customer identification and lookup
"""

from pydantic_ai import Agent, RunContext
from .dependencies import SharedDeps, CustomerResult

# ============================================================================
# CUSTOMER SPECIALIZED AGENT
# ============================================================================

customer_agent = Agent[SharedDeps, CustomerResult](
    'openai:gpt-4o',
    deps_type=SharedDeps,
    output_type=CustomerResult,
    instructions="""
    You are a CUSTOMER IDENTIFICATION SPECIALIST.
    Your ONLY job is to find customers by phone or email using LOFT API.
    
    RULES:
    1. Use search_customer tool for ALL customer lookups
    2. Return CustomerResult with structured data + HTML
    3. NEVER search products, orders, or anything else
    4. Be friendly: "Hello [Name]! How can I help you today?"
    """
)

@customer_agent.tool
async def search_customer(ctx: RunContext[SharedDeps], identifier: str, type: str = "auto") -> CustomerResult:
    """
    Find customer by phone or email in LOFT system
    
    Args:
        identifier: Phone number or email address
        type: "phone", "email", or "auto" to detect
    """
    
    print(f"🔧 CustomerAgent: Searching for {identifier} (type: {type})")
    
    # Auto-detect type if not specified
    if type == "auto":
        if "@" in identifier:
            type = "email"
        else:
            type = "phone"
    
    try:
        # Use shared HTTP client from dependency injection
        if type == "phone":
            url = f"{ctx.deps.loft_api_base}/GetCustomerByPhone"
            params = {'phone': identifier.strip()}
        else:  # email
            url = f"{ctx.deps.loft_api_base}/GetCustomerByEmail"  
            params = {'email': identifier.strip()}
        
        print(f"🌐 CustomerAgent: Calling {url}")
        response = await ctx.deps.http_client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"📊 CustomerAgent: Response {data}")
        
        # Parse LOFT API response
        if data and data.get('entry') and len(data['entry']) > 0:
            customer_data = data['entry'][0]
            
            # Extract customer info
            customer_id = customer_data.get('customerid', '')
            name = f"{customer_data.get('firstname', '')} {customer_data.get('lastname', '')}".strip()
            email = customer_data.get('email', '')
            phone = customer_data.get('phone', identifier if type == "phone" else '')
            
            # Generate HTML for display
            html = f"""
            <div class="customer-card">
                <h3>👤 Customer Found</h3>
                <p><strong>Hello {name}!</strong> Great to see you again.</p>
                <div class="customer-details">
                    <p>📱 {phone} | 🆔 ID: {customer_id} | 📧 {email}</p>
                </div>
                <p>How can I help you today?</p>
            </div>
            """
            
            return CustomerResult(
                found=True,
                customer_id=customer_id,
                name=name,
                email=email,
                phone=phone,
                html=html
            )
        else:
            return CustomerResult(
                found=False,
                html=f"<div class='error'>No customer found for {identifier}</div>"
            )
            
    except Exception as e:
        print(f"❌ CustomerAgent error: {e}")
        return CustomerResult(
            found=False,
            html=f"<div class='error'>Error searching for customer: {str(e)}</div>"
        )
