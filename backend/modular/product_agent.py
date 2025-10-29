"""
PRODUCT AGENT - 1 AGENT = 1 TOOL (Jorge's Pattern)  
Handles ONLY product search and catalog operations
"""

from pydantic_ai import Agent, RunContext
from .dependencies import SharedDeps, ProductResult
import json

# ============================================================================
# PRODUCT SPECIALIZED AGENT
# ============================================================================

product_agent = Agent[SharedDeps, ProductResult](
    'openai:gpt-4o',
    deps_type=SharedDeps,
    output_type=ProductResult,
    instructions="""
    You are a PRODUCT CATALOG SPECIALIST.
    Your ONLY job is to search and filter products using Magento API.
    
    RULES:
    1. Use product_search tool for ALL product-related queries
    2. Return ProductResult with structured data + CAROUSEL_DATA
    3. NEVER handle customers or orders - that's other agents' jobs
    4. Always suggest helpful filters: brand, color, price range
    """
)

@product_agent.tool
async def product_search(ctx: RunContext[SharedDeps], query: str, filters: dict = None, page_size: int = 8) -> ProductResult:
    """
    Search Magento products with optional filters
    
    Args:
        query: Search query ("grey sofas", "recliners under 1000")
        filters: Optional filters {"max_price": 1000, "brand": "Ashley"}
        page_size: Number of results to return
    """
    
    print(f"🔧 ProductAgent: Searching '{query}' with filters {filters}")
    
    try:
        # Get Magento authentication token
        token = await _get_magento_token(ctx)
        if not token:
            return ProductResult(
                found=False,
                query=query,
                html_carousel="<div class='error'>Product catalog unavailable</div>"
            )
        
        # Build search parameters for Magento API
        search_params = {
            'searchCriteria[pageSize]': str(page_size),
            'searchCriteria[currentPage]': '1',
            'searchCriteria[filterGroups][0][filters][0][field]': 'name',
            'searchCriteria[filterGroups][0][filters][0][value]': f'%{query}%',
            'searchCriteria[filterGroups][0][filters][0][conditionType]': 'like',
            'searchCriteria[filterGroups][1][filters][0][field]': 'status',
            'searchCriteria[filterGroups][1][filters][0][value]': '2',  # Enabled products
            'searchCriteria[filterGroups][1][filters][0][conditionType]': 'eq'
        }
        
        # Add price filter if specified
        if filters and filters.get('max_price'):
            search_params.update({
                'searchCriteria[filterGroups][2][filters][0][field]': 'price',
                'searchCriteria[filterGroups][2][filters][0][value]': str(filters['max_price']),
                'searchCriteria[filterGroups][2][filters][0][conditionType]': 'lte'
            })
        
        # Make API call
        url = f"{ctx.deps.magento_api_base}/rest/V1/products"
        response = await ctx.deps.http_client.get(
            url,
            params=search_params,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code != 200:
            return ProductResult(
                found=False,
                query=query,
                html_carousel=f"<div class='error'>Search failed: {response.status_code}</div>"
            )
        
        data = response.json()
        products = data.get('items', [])
        total_count = data.get('total_count', 0)
        
        if not products:
            return ProductResult(
                found=False,
                query=query,
                total_found=0,
                html_carousel=f"<div class='no-results'>No {query} found in our catalog</div>",
                suggested_filters=["Try different keywords", "Browse categories", "Check spelling"]
            )
        
        # Format products for carousel
        formatted_products = []
        carousel_items = []
        
        for i, product in enumerate(products[:page_size], 1):
            # Extract product info
            name = product.get('name', 'Product')
            sku = product.get('sku', '')
            price = product.get('price', 0)
            
            # Get product image
            image_url = 'https://via.placeholder.com/400x300/002147/FFFFFF?text=Woodstock+Furniture'
            if product.get('media_gallery_entries'):
                media = product['media_gallery_entries'][0]
                if media.get('file'):
                    image_file = media['file'].lstrip('/')
                    image_url = f"https://woodstockoutlet.com/media/catalog/product/{image_file}"
            
            # Structured product data
            product_data = {
                'position': i,
                'sku': sku,
                'name': name,
                'price': float(price),
                'image_url': image_url,
                'description': product.get('custom_attributes', [{}])[0].get('value', '')[:100]
            }
            formatted_products.append(product_data)
            
            # Carousel HTML item
            carousel_items.append(f"""
            <div class="product-card">
                <img src="{image_url}" alt="{name}" loading="lazy">
                <h4>{name}</h4>
                <p class="price">${price}</p>
                <p class="sku">SKU: {sku}</p>
            </div>
            """)
        
        # Generate CAROUSEL_DATA for frontend
        carousel_html = f"""
        CAROUSEL_DATA:
        <div class="product-carousel">
            <h3>🛒 {query.title()} - {len(products)} Found</h3>
            <div class="carousel-items">
                {''.join(carousel_items)}
            </div>
            <div class="carousel-controls">
                <p>💡 <strong>Helpful filters:</strong> Brand, Color, Price Range</p>
                <p>💬 Try: "show me the second one" or "filter by price under $500"</p>
            </div>
        </div>
        """
        
        return ProductResult(
            found=True,
            products=formatted_products,
            total_found=total_count,
            query=query,
            html_carousel=carousel_html,
            suggested_filters=["Brand", "Color", "Price Range", "Size", "Material"]
        )
        
    except Exception as e:
        print(f"❌ ProductAgent error: {e}")
        return ProductResult(
            found=False,
            query=query,
            html_carousel=f"<div class='error'>Product search error: {str(e)}</div>"
        )

async def _get_magento_token(ctx: RunContext[SharedDeps]) -> str:
    """Get Magento authentication token"""
    
    # Return cached token if available
    if ctx.deps.magento_token:
        return ctx.deps.magento_token
    
    # Get new token from environment or return None
    import os
    token = os.getenv('MAGENTO_ADMIN_TOKEN')
    if token:
        ctx.deps.magento_token = token  # Cache it
        return token
    
    print("⚠️ No Magento token available")
    return None
