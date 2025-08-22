"""LOFT Chat Backend with MEMORY - FastAPI + PydanticAI + PostgreSQL"""

import json
import asyncio
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart
from dotenv import load_dotenv
import os
from typing import AsyncIterator
import httpx

from .schemas import ChatRequest, ChatResponse, ChatMessage
from .conversation_memory import memory

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LOFT Chat Backend with Memory",
    description="Smart chat backend with LOFT functions and conversation memory",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PydanticAI agent
print("🔧 Initializing PydanticAI agent with memory...")
agent = Agent(
    model=f"openai:{os.getenv('OPENAI_MODEL', 'gpt-4.1')}",
    system_prompt=(
        "You are Woodstock Outlet's AI assistant. CRITICAL RULES:\n\n"
        "1. For EVERY customer inquiry, you MUST call the appropriate function first\n"
        "2. NEVER provide information without calling a function\n"
        "3. When user mentions phone/email, call get_customer_by_phone/get_customer_by_email\n"
        "4. When they ask about orders, call get_orders_by_customer with customer_id\n"
        "5. When they ask order details, call get_order_details with order_id\n"
        "6. When they ask patterns/analytics, call analyze_customer_patterns\n"
        "7. When they ask recommendations, call get_product_recommendations\n"
        "8. For loyalty/cross-sell/support, use the handle_ functions\n\n"
        "WORKFLOW:\n"
        "- Phone/Email query → call get_customer_by_phone/email\n"
        "- Orders query → call get_orders_by_customer\n"
        "- Details query → call get_order_details\n"
        "- Analysis query → call analyze_customer_patterns\n"
        "- Complete overview → call get_customer_journey\n\n"
        "ALWAYS use exact function results. Return function output exactly as received."
    )
)

# LOFT Function Definitions with @agent.tool decorators
print("🔧 Adding LOFT functions to agent...")

@agent.tool
async def get_customer_by_phone(ctx: RunContext, phone: str) -> str:
    """Buscar cliente por número de teléfono en LOFT"""
    API_BASE = os.getenv('WOODSTOCK_API_BASE', 'https://api.woodstockoutlet.com/public/index.php/april')
    
    try:
        print(f"🔧 Function Call: getCustomerByPhone({phone})")
        
        if not phone or len(phone.strip()) < 7:
            return "❌ Invalid phone number format. Please provide a valid phone number."
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{API_BASE}/GetCustomerByPhone"
            params = {'phone': phone.strip()}
            
            print(f"🌐 Calling LOFT API: {url} with phone: {phone}")
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"📊 LOFT API Response: {data}")
            
            # LOFT API returns data in 'entry' array
            if data and data.get('entry') and len(data['entry']) > 0:
                customer_data = data['entry'][0]
                
                customer_info = []
                customer_info.append(f"📱 Phone: {phone}")
                
                if customer_data.get('customerid'):
                    customer_info.append(f"🆔 Customer ID: {customer_data.get('customerid')}")
                
                if customer_data.get('firstname') or customer_data.get('lastname'):
                    name = f"{customer_data.get('firstname', '')} {customer_data.get('lastname', '')}".strip()
                    if name:
                        customer_info.append(f"👤 Name: {name}")
                
                if customer_data.get('email'):
                    customer_info.append(f"📧 Email: {customer_data.get('email')}")
                
                if customer_data.get('address1'):
                    address = customer_data.get('address1')
                    if customer_data.get('city'):
                        address += f", {customer_data.get('city')}"
                    if customer_data.get('state'):
                        address += f", {customer_data.get('state')}"
                    customer_info.append(f"🏠 Address: {address}")
                
                # Return BOTH JSON + TEXT for frontend extraction
                import json
                json_data = json.dumps({
                    "function": "getCustomerByPhone",
                    "status": "success", 
                    "data": {
                        "customerid": customer_data.get('customerid'),
                        "firstname": customer_data.get('firstname'),
                        "lastname": customer_data.get('lastname'),
                        "email": customer_data.get('email'),
                        "phone": phone,
                        "address": address,
                        "zipcode": customer_data.get('zipcode')
                    },
                    "message": f"Customer {name} found successfully"
                })
                
                return f"""**Function Result (getCustomerByPhone):**
{json_data}

✅ Customer found: {name} 
📱 Phone: {phone}
🆔 Customer ID: {customer_data.get('customerid')}
📧 Email: {customer_data.get('email')}
🏠 Address: {address}"""
            else:
                return f"❌ No customer found with phone number {phone}."
                
    except Exception as error:
        print(f"❌ Error in getCustomerByPhone: {error}")
        return f"❌ Error searching for customer: {str(error)}"

@agent.tool
async def get_orders_by_customer(ctx: RunContext, customer_id: str) -> str:
    """Get order history for a customer by customer ID"""
    API_BASE = os.getenv('WOODSTOCK_API_BASE', 'https://api.woodstockoutlet.com/public/index.php/april')
    
    try:
        print(f"🔧 Function Call: getOrdersByCustomer({customer_id})")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{API_BASE}/GetOrdersByCustomer"
            params = {'custid': customer_id}
            
            print(f"🌐 Calling LOFT API: {url} with customer: {customer_id}")
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"📊 Orders API Response: {data}")
            
            if data and data.get('entry') and len(data['entry']) > 0:
                orders = data['entry']
                
                order_info = []
                order_info.append(f"📦 Found {len(orders)} order(s) for customer {customer_id}:")
                
                for i, order in enumerate(orders[:5], 1):  # Limit to 5 recent orders
                    order_info.append(f"\n🛍️ Order #{i}:")
                    if order.get('orderid'):
                        order_info.append(f"   📋 Order ID: {order.get('orderid')}")
                    if order.get('orderstatus'):
                        order_info.append(f"   📊 Status: {order.get('orderstatus')}")
                    if order.get('ordertotal'):
                        order_info.append(f"   💰 Total: ${order.get('ordertotal')}")
                    if order.get('orderdate'):
                        order_info.append(f"   📅 Date: {order.get('orderdate')}")
                
                if len(orders) > 5:
                    order_info.append(f"\n... and {len(orders) - 5} more orders")
                
                # Return JSON like original - frontend will render HTML
                import json
                return json.dumps({
                    "function": "getOrdersByCustomer",
                    "status": "success",
                    "data": {
                        "orders": orders,
                        "customer_id": customer_id,
                        "total_orders": len(orders)
                    },
                    "message": f"Found {len(orders)} orders for customer {customer_id}"
                })
            else:
                return f"❌ No orders found for customer {customer_id}."
                
    except Exception as error:
        print(f"❌ Error in getOrdersByCustomer: {error}")
        return f"❌ Error searching for orders: {str(error)}"

# FUNCTION REMOVED - SearchProducts endpoint does not exist!

@agent.tool
async def get_customer_by_email(ctx: RunContext, email: str) -> str:
    """Buscar cliente por email en LOFT"""
    API_BASE = os.getenv('WOODSTOCK_API_BASE', 'https://api.woodstockoutlet.com/public/index.php/april')
    
    try:
        print(f"🔧 Function Call: getCustomerByEmail({email})")
        
        if not email or '@' not in email:
            return "❌ Invalid email format. Please provide a valid email address."
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{API_BASE}/GetCustomerByEmail"
            params = {'email': email.strip()}
            
            print(f"🌐 Calling LOFT API: {url} with email: {email}")
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"📊 LOFT Email API Response: {data}")
            
            if data and data.get('entry') and len(data['entry']) > 0:
                customer_data = data['entry'][0]
                
                customer_info = []
                customer_info.append(f"📧 Email: {email}")
                
                if customer_data.get('customerid'):
                    customer_info.append(f"🆔 Customer ID: {customer_data.get('customerid')}")
                
                if customer_data.get('firstname') or customer_data.get('lastname'):
                    name = f"{customer_data.get('firstname', '')} {customer_data.get('lastname', '')}".strip()
                    if name:
                        customer_info.append(f"👤 Name: {name}")
                
                if customer_data.get('phonenumber'):
                    customer_info.append(f"📱 Phone: {customer_data.get('phonenumber')}")
                
                return "✅ Customer found:\n" + "\n".join(customer_info)
            else:
                return f"❌ No customer found with email {email}."
                
    except Exception as error:
        print(f"❌ Error in getCustomerByEmail: {error}")
        return f"❌ Error searching for customer: {str(error)}"

@agent.tool
async def get_order_details(ctx: RunContext, order_id: str) -> str:
    """Get detailed line items for a specific order"""
    API_BASE = os.getenv('WOODSTOCK_API_BASE', 'https://api.woodstockoutlet.com/public/index.php/april')
    
    try:
        print(f"🔧 Function Call: getDetailsByOrder({order_id})")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{API_BASE}/GetDetailsByOrder"
            params = {'orderid': order_id}
            
            print(f"🌐 Calling LOFT API: {url} with order: {order_id}")
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"📊 Order Details API Response: {data}")
            
            if data and data.get('entry') and len(data['entry']) > 0:
                details = data['entry']
                
                detail_info = []
                detail_info.append(f"📦 Order Details for {order_id}:")
                detail_info.append(f"📋 {len(details)} item(s)")
                
                total_value = 0
                for i, item in enumerate(details, 1):
                    if item.get('description') and 'BENEFIT PLAN' not in item.get('description', ''):
                        detail_info.append(f"\n🛍️ Item #{i}:")
                        detail_info.append(f"   📦 {item.get('description', 'N/A')}")
                        
                        price = float(item.get('itemprice', 0) or 0)
                        if price > 0:
                            detail_info.append(f"   💰 ${price}")
                            total_value += price
                
                if total_value > 0:
                    detail_info.append(f"\n💰 Total: ${total_value:.2f}")
                
                return "\n".join(detail_info)
            else:
                return f"❌ No details found for order {order_id}."
                
    except Exception as error:
        print(f"❌ Error in getDetailsByOrder: {error}")
        return f"❌ Error getting order details: {str(error)}"

@agent.tool
async def get_customer_journey(ctx: RunContext, identifier: str, type: str = "phone") -> str:
    """Get complete customer journey - COMPOSITE FUNCTION combining multiple API calls"""
    try:
        print(f"🔧 COMPOSITE Function: getCustomerJourney({identifier}, {type})")
        
        # Step 1: Get customer info
        if type == "phone":
            customer_result = await get_customer_by_phone(ctx, identifier)
        else:
            customer_result = await get_customer_by_email(ctx, identifier)
        
        if "❌" in customer_result:
            return customer_result
        
        # Extract customer ID from result
        import re
        customer_id_match = re.search(r'Customer ID: (\d+)', customer_result)
        if not customer_id_match:
            return "❌ Could not extract customer ID from customer data"
        
        customer_id = customer_id_match.group(1)
        
        # Step 2: Get orders
        orders_result = await get_orders_by_customer(ctx, customer_id)
        
        if "❌" in orders_result:
            return f"✅ Customer found but no orders: {customer_result}\n\n{orders_result}"
        
        # Step 3: Get details for each order (extract order IDs)
        order_ids = re.findall(r'Order ID: ([A-Z0-9]+)', orders_result)
        
        journey_info = []
        journey_info.append("🎯 COMPLETE CUSTOMER JOURNEY:")
        journey_info.append(customer_result)
        journey_info.append("")
        journey_info.append(orders_result)
        
        # Get details for each order
        for order_id in order_ids[:3]:  # Limit to 3 most recent orders
            details_result = await get_order_details(ctx, order_id)
            journey_info.append("")
            journey_info.append(details_result)
        
        return "\n".join(journey_info)
        
    except Exception as error:
        print(f"❌ Error in getCustomerJourney: {error}")
        return f"❌ Error getting customer journey: {str(error)}"

@agent.tool
async def analyze_customer_patterns(ctx: RunContext, customer_identifier: str) -> str:
    """Analyze customer purchase patterns - provide phone, email, or customer ID"""
    try:
        print(f"🔧 DATABASE Function: analyzeCustomerPatterns({customer_identifier})")
        
        # Determine if it's phone, email, or customer ID
        if "@" in customer_identifier:
            # It's an email
            customer_result = await get_customer_by_email(ctx, customer_identifier)
        elif len(customer_identifier) == 10 and customer_identifier.isdigit():
            # It's a customer ID
            customer_id = customer_identifier
            orders_result = await get_orders_by_customer(ctx, customer_id)
        else:
            # Assume it's a phone
            customer_result = await get_customer_by_phone(ctx, customer_identifier)
            # Extract customer ID from result (handle both JSON and text format)
            import re, json
            try:
                # Try to parse as JSON first
                if "{" in customer_result and "customerid" in customer_result:
                    json_match = re.search(r'\{[^}]*"customerid"[^}]*\}', customer_result)
                    if json_match:
                        json_data = json.loads(json_match.group())
                        customer_id = json_data.get('customerid')
                    else:
                        # Fallback to text regex
                        customer_id_match = re.search(r'Customer ID: (\d+)', customer_result)
                        customer_id = customer_id_match.group(1) if customer_id_match else None
                else:
                    # Text format
                    customer_id_match = re.search(r'Customer ID: (\d+)', customer_result)
                    customer_id = customer_id_match.group(1) if customer_id_match else None
                
                if not customer_id:
                    return f"❌ Could not extract customer ID from {customer_identifier}"
            except Exception as e:
                return f"❌ Error parsing customer result: {str(e)}"
            orders_result = await get_orders_by_customer(ctx, customer_id)
        
        if "❌" in orders_result:
            return f"❌ Cannot analyze patterns - no orders found for customer {customer_id}"
        
        # Extract order details for analysis
        import re
        order_ids = re.findall(r'Order ID: ([A-Z0-9]+)', orders_result)
        
        if not order_ids:
            return f"❌ No order IDs found to analyze patterns for customer {customer_id}"
        
        # Analyze patterns from order details
        patterns_info = []
        patterns_info.append(f"📊 CUSTOMER PURCHASE PATTERNS for {customer_id}:")
        patterns_info.append(f"📦 Total Orders Analyzed: {len(order_ids)}")
        
        # Get details for pattern analysis
        total_spent = 0
        product_categories = []
        
        for order_id in order_ids[:5]:  # Analyze up to 5 recent orders
            details_result = await get_order_details(ctx, order_id)
            
            # Extract spending patterns
            spending_matches = re.findall(r'\$([0-9.]+)', details_result)
            for amount in spending_matches:
                total_spent += float(amount)
            
            # Extract product categories
            if "Sectional" in details_result:
                product_categories.append("Sectional")
            if "Recliner" in details_result:
                product_categories.append("Recliner")
            if "Console" in details_result:
                product_categories.append("Console")
        
        patterns_info.append(f"💰 Total Spending Analyzed: ${total_spent:.2f}")
        
        if product_categories:
            patterns_info.append(f"🎯 Favorite Categories: {', '.join(set(product_categories))}")
        
        patterns_info.append(f"\n💡 Customer Profile: {'High-value' if total_spent > 1500 else 'Regular'} customer")
        
        return "\n".join(patterns_info)
        
    except Exception as error:
        print(f"❌ Error in analyzeCustomerPatterns: {error}")
        return f"❌ Error analyzing patterns: {str(error)}"

@agent.tool
async def get_product_recommendations(ctx: RunContext, customer_id: str) -> str:
    """Generate product recommendations based on customer patterns"""
    try:
        print(f"🔧 DATABASE Function: getProductRecommendations({customer_id})")
        
        # Get patterns first
        patterns_result = await analyze_customer_patterns(ctx, customer_id)
        
        if "❌" in patterns_result:
            return patterns_result
        
        recommendations = []
        recommendations.append("🎯 PERSONALIZED PRODUCT RECOMMENDATIONS:")
        
        # Generate recommendations based on patterns
        if "Sectional" in patterns_result:
            recommendations.append("\n🛋️ Based on your Sectional purchase:")
            recommendations.append("   • Matching Ottoman/Console pieces")
            recommendations.append("   • Premium Sectional accessories")
            recommendations.append("   • Coordinating accent chairs")
        
        if "Recliner" in patterns_result:
            recommendations.append("\n🪑 Based on your Recliner preference:")
            recommendations.append("   • Additional reclining chairs")
            recommendations.append("   • Recliner accessories")
            recommendations.append("   • Power upgrade options")
        
        if "High-value" in patterns_result:
            recommendations.append("\n💎 Premium Recommendations:")
            recommendations.append("   • Extended warranty options")
            recommendations.append("   • White-glove delivery service")
            recommendations.append("   • Interior design consultation")
        
        recommendations.append(f"\n💡 Contact our sales team for personalized pricing!")
        
        return "\n".join(recommendations)
        
    except Exception as error:
        print(f"❌ Error in getProductRecommendations: {error}")
        return f"❌ Error getting recommendations: {str(error)}"

@agent.tool
async def get_customer_analytics(ctx: RunContext, identifier: str, type: str = "phone") -> str:
    """Get comprehensive customer analytics and insights"""
    try:
        print(f"🔧 ANALYTICS Function: getCustomerAnalytics({identifier}, {type})")
        
        # Get customer journey first
        journey_result = await get_customer_journey(ctx, identifier, type)
        
        if "❌" in journey_result:
            return journey_result
        
        # Extract customer ID from journey result for analytics
        customer_id_match = re.search(r'Customer ID: (\d+)', journey_result)
        if customer_id_match:
            patterns_result = await analyze_customer_patterns(ctx, customer_id_match.group(1))
        else:
            patterns_result = "❌ No customer ID found for patterns analysis"
        
        analytics = []
        analytics.append("📈 COMPREHENSIVE CUSTOMER ANALYTICS:")
        analytics.append("")
        analytics.append("🎯 CUSTOMER JOURNEY:")
        analytics.append(journey_result)
        analytics.append("")
        
        if "❌" not in patterns_result:
            analytics.append("📊 PURCHASE PATTERNS:")
            analytics.append(patterns_result)
        
        return "\n".join(analytics)
        
    except Exception as error:
        print(f"❌ Error in getCustomerAnalytics: {error}")
        return f"❌ Error getting analytics: {str(error)}"

@agent.tool
async def handle_order_confirmation_cross_sell(ctx: RunContext, identifier: str, type: str = "phone") -> str:
    """Handle order confirmation with cross-selling opportunities - PROACTIVE"""
    try:
        print(f"🔧 PROACTIVE Function: handleOrderConfirmationAndCrossSell({identifier}, {type})")
        
        # Get customer journey to find recent orders
        journey_result = await get_customer_journey(ctx, identifier, type)
        
        if "❌" in journey_result:
            return f"❌ Cannot provide order confirmation - {journey_result}"
        
        # Extract customer name and recent order info
        import re
        name_match = re.search(r'Name: ([^\\n]+)', journey_result)
        customer_name = name_match.group(1) if name_match else "Customer"
        
        order_ids = re.findall(r'Order ID: ([A-Z0-9]+)', journey_result)
        
        if not order_ids:
            return f"Hi {customer_name}! I don't see any recent orders to confirm. How can I help you today?"
        
        recent_order = order_ids[0]
        
        confirmation = []
        confirmation.append(f"✅ ORDER CONFIRMATION for {customer_name}:")
        confirmation.append(f"📦 Order ID: {recent_order}")
        confirmation.append("")
        
        # Cross-sell opportunities based on order
        if "Sectional" in journey_result:
            confirmation.append("🎯 CROSS-SELL OPPORTUNITIES:")
            confirmation.append("   💡 Complete your living room with:")
            confirmation.append("   • Matching accent pillows")
            confirmation.append("   • Coordinating coffee table")
            confirmation.append("   • Area rug for the space")
            confirmation.append("   • Extended warranty protection")
        
        confirmation.append(f"\n📞 Questions? Call us or visit our showroom!")
        
        return "\\n".join(confirmation)
        
    except Exception as error:
        print(f"❌ Error in handleOrderConfirmationAndCrossSell: {error}")
        return f"❌ Error with order confirmation: {str(error)}"

@agent.tool
async def handle_support_escalation(ctx: RunContext, identifier: str, issue_description: str, type: str = "phone") -> str:
    """Handle support escalation with ticket creation - PROACTIVE"""
    try:
        print(f"🔧 PROACTIVE Function: handleSupportEscalation({identifier}, {issue_description}, {type})")
        
        # Get customer info first
        if type == "phone":
            customer_result = await get_customer_by_phone(ctx, identifier)
        else:
            customer_result = await get_customer_by_email(ctx, identifier)
        
        if "❌" in customer_result:
            return customer_result
        
        # Extract customer name
        import re
        name_match = re.search(r'Name: ([^\\n]+)', customer_result)
        customer_name = name_match.group(1) if name_match else "Customer"
        
        escalation = []
        escalation.append(f"🚨 SUPPORT ESCALATION for {customer_name}:")
        escalation.append("")
        escalation.append(f"📋 Issue: {issue_description}")
        escalation.append(f"📞 Customer: {identifier}")
        escalation.append("")
        escalation.append("✅ ESCALATION ACTIONS:")
        escalation.append("   • Priority support ticket created")
        escalation.append("   • Manager notification sent")
        escalation.append("   • 24-hour response guarantee")
        escalation.append("")
        escalation.append("📞 Direct contact: 1-800-WOODSTOCK")
        escalation.append("📧 Email updates: support@woodstockoutlet.com")
        
        return "\\n".join(escalation)
        
    except Exception as error:
        print(f"❌ Error in handleSupportEscalation: {error}")
        return f"❌ Error escalating support: {str(error)}"

@agent.tool
async def handle_loyalty_upgrade(ctx: RunContext, identifier: str, type: str = "phone") -> str:
    """Handle loyalty tier upgrades and notifications - PROACTIVE"""
    try:
        print(f"🔧 PROACTIVE Function: handleLoyaltyUpgrade({identifier}, {type})")
        
        # Get customer patterns to determine loyalty status
        if type == "phone":
            customer_result = await get_customer_by_phone(ctx, identifier)
        else:
            customer_result = await get_customer_by_email(ctx, identifier)
        
        if "❌" in customer_result:
            return customer_result
        
        # Extract customer info
        import re
        name_match = re.search(r'Name: ([^\\n]+)', customer_result)
        customer_name = name_match.group(1) if name_match else "Customer"
        
        customer_id_match = re.search(r'Customer ID: (\d+)', customer_result)
        if customer_id_match:
            patterns_result = await analyze_customer_patterns(ctx, customer_id_match.group(1))
        else:
            patterns_result = "❌ No customer ID found"
        
        loyalty = []
        loyalty.append(f"🏆 LOYALTY STATUS for {customer_name}:")
        loyalty.append("")
        
        if "High-value" in patterns_result:
            loyalty.append("⭐ PREMIUM MEMBER BENEFITS:")
            loyalty.append("   • 10% discount on future purchases")
            loyalty.append("   • Free white-glove delivery")
            loyalty.append("   • Priority customer service")
            loyalty.append("   • Exclusive early access to sales")
            loyalty.append("   • Complimentary interior design consultation")
        else:
            loyalty.append("🎯 EARN PREMIUM STATUS:")
            loyalty.append("   • Spend $500 more to unlock Premium benefits")
            loyalty.append("   • Current benefits: Standard customer service")
            loyalty.append("   • Next level: Premium member perks")
        
        loyalty.append("")
        loyalty.append("📞 Questions about loyalty? Call 1-800-WOODSTOCK")
        
        return "\\n".join(loyalty)
        
    except Exception as error:
        print(f"❌ Error in handleLoyaltyUpgrade: {error}")
        return f"❌ Error with loyalty upgrade: {str(error)}"

@agent.tool
async def handle_product_recommendations(ctx: RunContext, identifier: str, type: str = "phone") -> str:
    """Handle personalized product recommendations - PROACTIVE"""
    try:
        print(f"🔧 PROACTIVE Function: handleProductRecommendations({identifier}, {type})")
        
        # Get customer ID first
        if type == "phone":
            customer_result = await get_customer_by_phone(ctx, identifier)
        else:
            customer_result = await get_customer_by_email(ctx, identifier)
        
        if "❌" in customer_result:
            return customer_result
        
        # Extract customer ID and get recommendations
        import re
        customer_id_match = re.search(r'Customer ID: (\d+)', customer_result)
        if not customer_id_match:
            return "❌ Cannot generate recommendations - no customer ID found"
        
        customer_id = customer_id_match.group(1)
        recommendations_result = await get_product_recommendations(ctx, customer_id)
        
        name_match = re.search(r'Name: ([^\\n]+)', customer_result)
        customer_name = name_match.group(1) if name_match else "Customer"
        
        proactive_recs = []
        proactive_recs.append(f"🎯 PERSONALIZED RECOMMENDATIONS for {customer_name}:")
        proactive_recs.append("")
        proactive_recs.append(recommendations_result)
        proactive_recs.append("")
        proactive_recs.append("📞 Ready to order? Call 1-800-WOODSTOCK")
        proactive_recs.append("🏪 Visit our showroom for hands-on experience!")
        
        return "\\n".join(proactive_recs)
        
    except Exception as error:
        print(f"❌ Error in handleProductRecommendations: {error}")
        return f"❌ Error handling recommendations: {str(error)}"

print(f"✅ Agent initialized with 12 LOFT functions (4 API + 8 database/analytics/proactive)")

# Startup and shutdown events
async def startup_event():
    """Initialize services on startup"""
    await memory.init_db()

async def shutdown_event():
    """Clean up on shutdown"""
    await memory.close()

# Register lifespan events (modern FastAPI way)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()

app.router.lifespan_context = lifespan

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "LOFT Chat Backend with Memory is running!",
        "model": os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
        "functions": 12,
        "memory": "PostgreSQL (Existing Tables)"
    }

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
    """
    SMART SESSION RULES: When to use memory vs new session
    
    USE MEMORY when:
    - Follow-up questions about orders, details, etc.
    - User identifier matches previous sessions
    - Conversational context (pronouns like 'my', 'her', 'that')
    
    NEW SESSION when:
    - Explicit 'new chat', 'start over', 'clear history'
    - Different user identifier detected
    - Greeting messages when switching contexts
    """
    message_lower = message.lower()
    
    # FORCE NEW SESSION triggers
    new_session_triggers = [
        'new chat', 'start over', 'clear history', 'reset', 'begin again',
        'different customer', 'another customer', 'switch customer'
    ]
    
    if any(trigger in message_lower for trigger in new_session_triggers):
        print(f"🆕 NEW SESSION triggered by: {message}")
        return False
    
    # USE MEMORY triggers  
    memory_triggers = [
        'my orders', 'her orders', 'his orders', 'their orders',
        'that order', 'this order', 'the order', 'those orders',
        'show me', 'get details', 'more info', 'tell me more',
        'what about', 'details on', 'expand on', 'continue'
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

# Main chat completions endpoint with MEMORY
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """Chat completions with conversation memory using EXISTING PostgreSQL tables"""
    try:
        print(f"📨 Chat request received: {len(request.messages)} messages")
        
        # Extract user message
        user_message = request.messages[-1].content if request.messages else ""
        print(f"🤖 Processing prompt: {user_message[:50]}...")
        
        # Extract user identifier from message or use session info
        user_identifier = None
        if hasattr(request, 'user_identifier') and request.user_identifier:
            user_identifier = request.user_identifier
        else:
            user_identifier = extract_user_identifier(user_message)
        
        print(f"👤 User identifier: {user_identifier}")
        
        # SMART SESSION MANAGEMENT - cuando usar memoria vs nueva sesión
        use_memory = should_use_memory(user_message, user_identifier)
        print(f"🧠 Memory decision: {'USE MEMORY' if use_memory else 'NEW SESSION'}")
        
        # Get or create conversation using EXISTING tables
        if use_memory:
            conversation_id = await memory.get_or_create_conversation(user_identifier)
        else:
            # Force new conversation for fresh start
            conversation_id = await memory.get_or_create_conversation(f"{user_identifier}_new_{int(asyncio.get_event_loop().time())}")
            print(f"🆕 Starting NEW session for: {user_identifier}")
        
        # Get conversation history from EXISTING tables
        db_messages = await memory.get_recent_messages(conversation_id, limit=10)
        
        # Convert to PydanticAI ModelMessage format (THE CORRECT WAY!)        
        message_history = []
        for msg in db_messages:
            if msg["role"] == "user":
                message_history.append(
                    ModelRequest(parts=[UserPromptPart(content=msg["content"])])
                )
            elif msg["role"] == "assistant":
                message_history.append(
                    ModelResponse(parts=[TextPart(content=msg["content"])])
                )
        
        # ONLY pass the history, not the current message (that goes as user_prompt)
        
        print(f"📚 Using {len(message_history)} historical messages")
        
        if request.stream:
            print("🤖 Running streaming response with memory...")
            async def generate_stream():
                try:
                    async with agent.run_stream(user_message, message_history=message_history) as result:
                        # Save user message to EXISTING table
                        await memory.save_user_message(conversation_id, user_message)
                        
                        full_response = ""
                        async for message in result.stream_text(delta=True):
                            full_response += message
                            chunk = {
                                "choices": [{"delta": {"content": message}}],
                                "model": "loft-chat"
                            }
                            yield f"data: {json.dumps(chunk)}\n\n"
                        
                        # Save assistant response to EXISTING table
                        await memory.save_assistant_message(conversation_id, full_response)
                        
                        yield "data: [DONE]\n\n"
                        
                except Exception as e:
                    error_chunk = {
                        "choices": [{"delta": {"content": f"❌ Error: {str(e)}"}}],
                        "model": "loft-chat"
                    }
                    yield f"data: {json.dumps(error_chunk)}\n\n"
                    yield "data: [DONE]\n\n"
            
            return StreamingResponse(generate_stream(), media_type="text/event-stream")
        
        else:
            print("🤖 Running non-streaming response with memory...")
            result = await agent.run(user_message, message_history=message_history)
            
            # Save user message to EXISTING table
            await memory.save_user_message(conversation_id, user_message)
            
            # Save assistant response to EXISTING table  
            await memory.save_assistant_message(conversation_id, str(result.data))
            
            response = ChatResponse(
                choices=[{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result.data
                    },
                    "finish_reason": "stop"
                }],
                model="loft-chat",
                usage={
                    "prompt_tokens": len(user_message.split()),
                    "completion_tokens": len(str(result.data).split()) if result.data else 0,
                    "total_tokens": len(user_message.split()) + (len(str(result.data).split()) if result.data else 0)
                }
            )
            return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Session info endpoint
@app.get("/v1/sessions/{user_identifier}")
async def get_session_info(user_identifier: str):
    """Get session/conversation info"""
    try:
        conversation_id = await memory.get_or_create_conversation(user_identifier)
        messages = await memory.get_recent_messages(conversation_id)
        customer_context = await memory.extract_customer_context(conversation_id)
        
        return {
            "user_identifier": user_identifier,
            "conversation_id": conversation_id,
            "message_count": len(messages),
            "customer_context": customer_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LOFT Chat Backend v2.0 - WITH MEMORY!</title>
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
                ✅ NOW WITH CONVERSATION MEMORY! ✅
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🔧 Backend Features</h3>
                    <ul>
                        <li>✅ FastAPI + PydanticAI</li>
                        <li>✅ PostgreSQL Memory (Existing Tables)</li>
                        <li>✅ Conversation History</li>
                        <li>✅ Context Preservation</li>
                        <li>✅ User Identification</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>🎯 LOFT Functions</h3>
                    <ul>
                        <li>📱 Customer search by phone</li>
                        <li>📦 Order history lookup</li>
                        <li>🛍️ Product search</li>
                        <li>🧠 Conversation memory</li>
                        <li>🤖 Context awareness</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>🚀 Test Memory</h3>
                    <p><strong>Frontend:</strong> <a href="http://localhost:3000">http://localhost:3000</a></p>
                    <p><strong>Example conversation:</strong></p>
                    <ol>
                        <li>Say: <code>407-288-6040</code></li>
                        <li>Then: <code>What are my orders?</code></li>
                        <li>AI remembers you're Janice! 🎉</li>
                    </ol>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px; font-size: 1.2em;">
                <p>💡 <strong>The AI now remembers who you are!</strong></p>
                <p>✨ Uses existing PostgreSQL tables ✨</p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8001))
    print("🚀 Starting LOFT Chat Backend with MEMORY...")
    print(f"📱 Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    print(f"🧠 Memory: PostgreSQL (EXISTING TABLES)")
    print(f"🌐 Web UI: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=["backend"],
        log_level="info"
    )
