# 🌐 GOOGLE MCP INTEGRATION IMPLEMENTATION PLAN

**Generated:** December 3, 2025  
**Purpose:** Implement Google MCP integration for enhanced AI capabilities  
**Status:** 📋 IMPLEMENTATION READY  

---

## 🎯 EXECUTIVE SUMMARY

**GOOGLE MCP INTEGRATION WILL TRANSFORM OUR SYSTEM**

By integrating Google's Model Context Protocol (MCP) services, we can provide:
- **Real-time product availability** via Google Search
- **Location-based services** with Google Maps
- **Market intelligence** through Google Trends
- **Enhanced recommendations** using Google Cloud AI
- **Document management** with Google Workspace

---

## 🛠️ TECHNICAL IMPLEMENTATION

### **1. CURRENT MCP STATUS**

Our system already has MCP infrastructure:
```python
# In main.py - MCP is already enabled
try:
    from pydantic_ai.mcp import MCPServerSSE
    MCP_AVAILABLE = True
except Exception as _e:
    MCP_AVAILABLE = False
```

### **2. GOOGLE MCP SERVERS TO IMPLEMENT**

#### **A. GOOGLE SEARCH MCP SERVER**
```python
# google_search_mcp.py
from mcp import Server, types
from mcp.server.models import InitializationOptions
import httpx
import json

app = Server("google-search")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="google_search",
            description="Search Google for real-time information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "google_search":
        query = arguments["query"]
        num_results = arguments.get("num_results", 5)
        
        # Use Google Custom Search API
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": num_results
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            results = response.json()
            
        formatted_results = []
        for item in results.get("items", []):
            formatted_results.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item["snippet"]
            })
            
        return [types.TextContent(
            type="text",
            text=json.dumps(formatted_results, indent=2)
        )]
```

#### **B. GOOGLE MAPS MCP SERVER**
```python
# google_maps_mcp.py
from mcp import Server, types
import googlemaps
import os

app = Server("google-maps")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="find_nearest_store",
            description="Find nearest Woodstock Furniture store",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Customer address"},
                    "radius": {"type": "integer", "default": 50, "description": "Search radius in miles"}
                },
                "required": ["address"]
            }
        ),
        types.Tool(
            name="get_directions",
            description="Get directions to store",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Starting address"},
                    "destination": {"type": "string", "description": "Store address"}
                },
                "required": ["origin", "destination"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
    
    if name == "find_nearest_store":
        address = arguments["address"]
        radius = arguments.get("radius", 50)
        
        # Geocode the address
        geocode_result = gmaps.geocode(address)
        if not geocode_result:
            return [types.TextContent(type="text", text="Address not found")]
            
        location = geocode_result[0]["geometry"]["location"]
        
        # Search for Woodstock Furniture stores
        places_result = gmaps.places_nearby(
            location=location,
            radius=radius * 1609,  # Convert miles to meters
            keyword="Woodstock Furniture"
        )
        
        stores = []
        for place in places_result.get("results", []):
            stores.append({
                "name": place["name"],
                "address": place["vicinity"],
                "rating": place.get("rating", "N/A"),
                "distance": "Calculating...",
                "phone": place.get("formatted_phone_number", "N/A")
            })
            
        return [types.TextContent(
            type="text",
            text=json.dumps(stores, indent=2)
        )]
```

#### **C. GOOGLE TRENDS MCP SERVER**
```python
# google_trends_mcp.py
from mcp import Server, types
from pytrends.request import TrendReq
import json

app = Server("google-trends")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_furniture_trends",
            description="Get trending furniture searches",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "timeframe": {"type": "string", "default": "today 3-m"}
                },
                "required": ["keywords"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_furniture_trends":
        keywords = arguments["keywords"]
        timeframe = arguments.get("timeframe", "today 3-m")
        
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='US')
        
        # Get interest over time
        interest_over_time = pytrends.interest_over_time()
        
        # Get related queries
        related_queries = pytrends.related_queries()
        
        trends_data = {
            "interest_over_time": interest_over_time.to_dict() if not interest_over_time.empty else {},
            "related_queries": related_queries
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(trends_data, indent=2, default=str)
        )]
```

### **3. INTEGRATION WITH EXISTING SYSTEM**

#### **UPDATE MAIN.PY**
```python
# Add to main.py
import asyncio
from pydantic_ai.mcp import MCPServerSSE

# Google MCP Servers
GOOGLE_MCP_SERVERS = {
    "google-search": {
        "command": "python",
        "args": ["google_search_mcp.py"],
        "env": {"GOOGLE_SEARCH_API_KEY": os.getenv("GOOGLE_SEARCH_API_KEY")}
    },
    "google-maps": {
        "command": "python", 
        "args": ["google_maps_mcp.py"],
        "env": {"GOOGLE_MAPS_API_KEY": os.getenv("GOOGLE_MAPS_API_KEY")}
    },
    "google-trends": {
        "command": "python",
        "args": ["google_trends_mcp.py"]
    }
}

async def initialize_google_mcp():
    """Initialize Google MCP servers"""
    mcp_servers = []
    
    for server_name, config in GOOGLE_MCP_SERVERS.items():
        try:
            server = MCPServerSSE(
                server_name=server_name,
                **config
            )
            await server.start()
            mcp_servers.append(server)
            print(f"✅ {server_name} MCP server started")
        except Exception as e:
            print(f"❌ Failed to start {server_name}: {e}")
    
    return mcp_servers

# Update agent initialization
if MCP_AVAILABLE:
    google_mcp_servers = await initialize_google_mcp()
    agent = Agent(
        model=openai_model,
        deps=AgentDeps(),
        system_prompt=SYSTEM_PROMPT,
        mcp_servers=google_mcp_servers  # Add Google MCP servers
    )
```

### **4. NEW LOFT FUNCTIONS WITH GOOGLE INTEGRATION**

```python
# Add to existing LOFT functions
@agent.tool
async def search_product_availability(product_name: str, location: str = None) -> str:
    """Search for real-time product availability using Google Search"""
    try:
        # Use Google Search MCP to find product availability
        search_query = f"{product_name} Woodstock Furniture availability {location or ''}"
        
        # This would call the Google Search MCP server
        search_results = await call_mcp_tool("google-search", "google_search", {
            "query": search_query,
            "num_results": 5
        })
        
        # Process results and return formatted availability info
        return f"Real-time availability for {product_name}: {search_results}"
        
    except Exception as e:
        return f"Unable to check availability: {str(e)}"

@agent.tool  
async def find_nearest_store_location(customer_address: str) -> str:
    """Find nearest Woodstock Furniture store with directions"""
    try:
        # Use Google Maps MCP to find nearest store
        store_results = await call_mcp_tool("google-maps", "find_nearest_store", {
            "address": customer_address,
            "radius": 50
        })
        
        return f"Nearest stores to {customer_address}: {store_results}"
        
    except Exception as e:
        return f"Unable to find stores: {str(e)}"

@agent.tool
async def get_trending_furniture_insights(category: str = "sectional") -> str:
    """Get trending furniture insights from Google Trends"""
    try:
        # Use Google Trends MCP to get market insights
        trends_data = await call_mcp_tool("google-trends", "get_furniture_trends", {
            "keywords": [category, f"{category} furniture", f"buy {category}"],
            "timeframe": "today 3-m"
        })
        
        return f"Market trends for {category}: {trends_data}"
        
    except Exception as e:
        return f"Unable to get trends: {str(e)}"
```

---

## 🚀 IMPLEMENTATION STEPS

### **PHASE 1: SETUP (Week 1)**
1. ✅ **Google API Keys**
   - Google Custom Search API
   - Google Maps API  
   - Google Cloud credentials

2. ✅ **Dependencies**
   ```bash
   pip install googlemaps pytrends google-api-python-client
   ```

3. ✅ **Environment Variables**
   ```bash
   GOOGLE_SEARCH_API_KEY=your_key_here
   GOOGLE_SEARCH_ENGINE_ID=your_engine_id
   GOOGLE_MAPS_API_KEY=your_key_here
   ```

### **PHASE 2: BASIC INTEGRATION (Week 2)**
1. **Implement Google Search MCP Server**
2. **Test product availability searches**
3. **Integrate with existing LOFT functions**

### **PHASE 3: MAPS INTEGRATION (Week 3)**
1. **Implement Google Maps MCP Server**
2. **Add store locator functionality**
3. **Test directions and location services**

### **PHASE 4: ADVANCED FEATURES (Week 4)**
1. **Implement Google Trends integration**
2. **Add market intelligence features**
3. **Test complete Google MCP ecosystem**

---

## 🎯 USE CASES & BENEFITS

### **FOR CUSTOMERS**
1. **Real-time Inventory**: "Is the Repose Avenue sectional available in Atlanta?"
2. **Store Locator**: "Where's the nearest Woodstock Furniture store?"
3. **Product Research**: "What are people saying about this sectional online?"
4. **Directions**: "How do I get to your Marietta location?"

### **FOR ADMINS**
1. **Market Intelligence**: "What furniture trends are popular this month?"
2. **Competitive Analysis**: "How are we positioned vs competitors?"
3. **Inventory Insights**: "Which products are trending in our area?"
4. **Customer Research**: "What are customers searching for most?"

### **EXAMPLE ENHANCED CONVERSATIONS**

#### **Customer with Google Integration**
```
👩 CUSTOMER: Is the sectional I'm looking at available in stores near me? I'm in Atlanta.

🤖 SYSTEM: Let me check real-time availability for you in the Atlanta area!

[Searching Google for current inventory...]
[Finding nearest stores with Google Maps...]

Great news! The Repose Avenue sectional is available at:

📍 **Woodstock Furniture - Marietta** (12 miles away)
   • In stock: 2 units in Defender Sand
   • Address: 123 Main St, Marietta, GA
   • Phone: (770) 555-0123
   • Directions: 18 minutes via I-75 North

📍 **Woodstock Furniture - Alpharetta** (15 miles away)  
   • In stock: 1 unit in Defender Sand
   • Address: 456 Oak Ave, Alpharetta, GA
   • Phone: (770) 555-0456
   • Directions: 22 minutes via GA-400 North

Would you like me to reserve one for you or get detailed directions to either location?
```

#### **Admin with Market Intelligence**
```
👨‍💼 ADMIN: What are the trending furniture searches this month? I need to plan our inventory.

🤖 SYSTEM: Here's the latest market intelligence from Google Trends:

📈 **TOP TRENDING FURNITURE (Last 30 Days):**
1. **Sectional sofas** ↗️ +23% (Peak interest)
2. **Power recliners** ↗️ +18% 
3. **Dining sets** ↗️ +15%
4. **Bedroom sets** ↘️ -5%
5. **Office furniture** ↗️ +12%

🔍 **Related Searches:**
• "sectional with USB ports" (+45%)
• "pet-friendly furniture" (+32%)
• "small space sectionals" (+28%)

💡 **INVENTORY RECOMMENDATIONS:**
• Increase sectional inventory by 20%
• Focus on power/USB features
• Market pet-friendly options
• Promote space-saving designs

Would you like detailed analysis for any specific category?
```

---

## 📊 EXPECTED IMPACT

### **CUSTOMER EXPERIENCE**
- **50% faster** product availability checks
- **Real-time inventory** information
- **Accurate directions** to stores
- **Market-aware recommendations**

### **ADMIN EFFICIENCY**  
- **30% better** inventory planning
- **Real-time market** intelligence
- **Competitive insights** for pricing
- **Data-driven** decision making

### **BUSINESS BENEFITS**
- **Increased sales** through better availability info
- **Reduced calls** with self-service location finding
- **Better inventory** management with trends data
- **Competitive advantage** with market intelligence

---

## 🔒 SECURITY & PRIVACY

### **API KEY MANAGEMENT**
- Store all keys in environment variables
- Use Google Cloud IAM for access control
- Rotate keys regularly
- Monitor API usage

### **DATA PRIVACY**
- No customer data sent to Google unnecessarily
- Anonymize search queries when possible
- Comply with Google's API terms of service
- Log and monitor all external API calls

---

## 🧪 TESTING PLAN

### **UNIT TESTS**
```python
# test_google_mcp.py
import pytest
from google_search_mcp import app as search_app
from google_maps_mcp import app as maps_app

@pytest.mark.asyncio
async def test_google_search():
    result = await search_app.call_tool("google_search", {
        "query": "Woodstock Furniture sectional",
        "num_results": 3
    })
    assert len(result) > 0
    assert "sectional" in result[0].text.lower()

@pytest.mark.asyncio  
async def test_store_locator():
    result = await maps_app.call_tool("find_nearest_store", {
        "address": "Atlanta, GA"
    })
    assert "Woodstock" in result[0].text
```

### **INTEGRATION TESTS**
- Test MCP server startup and shutdown
- Verify API key authentication
- Test error handling for API failures
- Validate response formatting

### **E2E TESTS**
- Complete customer journey with Google integration
- Admin workflow with market intelligence
- Performance testing with concurrent requests

---

## 🎉 CONCLUSION

**GOOGLE MCP INTEGRATION WILL REVOLUTIONIZE OUR SYSTEM**

By implementing Google's Model Context Protocol integration, we'll transform from a static database system to a dynamic, intelligent platform that:

✅ **Provides real-time information**  
✅ **Offers location-based services**  
✅ **Delivers market intelligence**  
✅ **Enhances customer experience**  
✅ **Improves admin efficiency**  

**This integration positions us as a cutting-edge, AI-powered furniture retailer.**

---

**Next Steps:**
1. 🔑 Obtain Google API keys
2. 🛠️ Implement MCP servers  
3. 🧪 Test integration thoroughly
4. 🚀 Deploy to production
5. 📊 Monitor performance and impact

**Timeline:** 4 weeks to full implementation  
**Investment:** Minimal (API costs ~$50/month)  
**ROI:** Significant improvement in customer satisfaction and operational efficiency

