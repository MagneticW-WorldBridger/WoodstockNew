# 🚀 COMPLETE FUNCTION TESTING GUIDE - ALL 30+ ENDPOINTS
## **COMPREHENSIVE CONVERSATION TESTING FOR ALL LOFT + MAGENTO + MEMORY FUNCTIONS**

**Updated:** October 3, 2025  
**Purpose:** Test EVERY SINGLE function with conversation examples  
**Status:** 🔥 **READY FOR COMPLETE TESTING** 🔥  

---

## 🎯 **TESTING ACCESS:**

### **Frontend URL:**
```
https://woodstocknew-production.up.railway.app/frontend/
```

### **Backend API:**
```
https://woodstocknew-production.up.railway.app
```

### **Health Check:**
```
https://woodstocknew-production.up.railway.app/health
```

---

## 🧪 **ALL 30+ FUNCTIONS - CONVERSATION EXAMPLES**

### **📱 CUSTOMER FUNCTIONS (LOFT API - 14 Functions):**

#### **1. get_customer_by_phone** ✅
```
CONVERSATION: "My phone number is 407-288-6040"
EXPECTED: Customer recognition + greeting
COMPONENT: Customer Profile Card
```

#### **2. get_customer_by_email** ✅
```
CONVERSATION: "My email is jdan4sure@yahoo.com"
EXPECTED: Customer identification 
COMPONENT: Customer Profile Card
```

#### **3. get_orders_by_customer** ✅
```
CONVERSATION: "Show me my order history"
EXPECTED: Order history display
COMPONENT: Order History Card
```

#### **4. get_order_details** ✅
```
CONVERSATION: "Show me details for order 0710544II27"
EXPECTED: Itemized order breakdown
COMPONENT: Order Details Card
```

#### **5. get_customer_journey** ✅
```
CONVERSATION: "Show my complete customer journey"
EXPECTED: Timeline of interactions
COMPONENT: Customer Journey Card
```

#### **6. analyze_customer_patterns** ✅
```
CONVERSATION: "Analyze patterns for customer 9318667506"
EXPECTED: Analytics dashboard
COMPONENT: Customer Patterns Card
```

#### **7. get_product_recommendations** ✅
```
CONVERSATION: "What products do you recommend for me?"
EXPECTED: Personalized recommendations
COMPONENT: Product Recommendations Grid
```

#### **8. get_customer_analytics** ✅
```
CONVERSATION: "Show customer analytics for 407-288-6040"
EXPECTED: Customer analytics dashboard
COMPONENT: Analytics Dashboard
```

#### **9. handle_order_confirmation_cross_sell** ✅
```
CONVERSATION: "I just placed an order, any suggestions?"
EXPECTED: Cross-sell opportunities
COMPONENT: Cross-sell Recommendations
```

#### **10. handle_support_escalation** ✅
```
CONVERSATION: "I need help with a return, my recliner arrived damaged"
EXPECTED: Support ticket creation + escalation
COMPONENT: Support Ticket Card
```

#### **11. handle_loyalty_upgrade** ✅
```
CONVERSATION: "How is my loyalty status?"
EXPECTED: Loyalty program information
COMPONENT: Loyalty Status Card
```

#### **12. handle_product_recommendations** ✅
```
CONVERSATION: "Based on my history, what should I buy?"
EXPECTED: AI-powered recommendations
COMPONENT: Smart Recommendations Grid
```

#### **13. connect_to_support** ✅
```
CONVERSATION: "I need to speak to someone"
EXPECTED: Human support connection
COMPONENT: Support Connection Card
```

#### **14. show_directions** ✅
```
CONVERSATION: "How do I get to your store in Acworth?"
EXPECTED: Store directions + map
COMPONENT: Directions Card
```

---

### **🛒 PRODUCT DISCOVERY FUNCTIONS (MAGENTO API - 16 Functions):**

#### **15. search_magento_products** ✅
```
CONVERSATION: "Show me sectional sofas"
EXPECTED: Product search results + carousel
COMPONENT: Product Carousel
```

#### **16. get_all_furniture_brands** ✅
```
CONVERSATION: "What brands do you carry?"
EXPECTED: Complete brand list (450+ brands)
COMPONENT: Brand Grid Display
```

#### **17. get_all_furniture_colors** ✅
```
CONVERSATION: "What colors are available?"
EXPECTED: Color options display
COMPONENT: Color Palette Grid
```

#### **18. search_products_by_price_range** ✅
```
CONVERSATION: "Show me recliners under $500"
EXPECTED: Budget-filtered products
COMPONENT: Budget Product Grid
```

#### **19. search_products_by_brand_and_category** ✅
```
CONVERSATION: "Show me Ashley sectionals"
EXPECTED: Brand + category filtered products
COMPONENT: Filtered Product Carousel
```

#### **20. get_product_photos** ✅
```
CONVERSATION: "Show me photos of SKU 1234567890"
EXPECTED: Photo gallery for product
COMPONENT: Photo Gallery Carousel
```

#### **21. get_featured_best_seller_products** ✅
```
CONVERSATION: "What are your best sellers?"
EXPECTED: Featured products display
COMPONENT: Best Sellers Grid
```

#### **22. show_sectional_products** ✅
```
CONVERSATION: "Show me sectionals"
EXPECTED: Sectional category products
COMPONENT: Sectional Product Grid
```

#### **23. show_recliner_products** ✅
```
CONVERSATION: "Show me recliners"
EXPECTED: Recliner category products
COMPONENT: Recliner Product Grid
```

#### **24. show_dining_products** ✅
```
CONVERSATION: "Show me dining room furniture"
EXPECTED: Dining category products  
COMPONENT: Dining Product Grid
```

#### **25. get_magento_product_by_sku** ✅
```
CONVERSATION: "Tell me about product SKU 1234567890"
EXPECTED: Single product details
COMPONENT: Product Detail Card
```

#### **26. get_magento_categories** ✅
```
CONVERSATION: "What product categories do you have?"
EXPECTED: Category hierarchy
COMPONENT: Category Tree Display
```

#### **27. get_magento_customer_by_email** ✅
```
CONVERSATION: "Look up Magento customer jdan4sure@yahoo.com"
EXPECTED: Magento customer data
COMPONENT: Magento Customer Card
```

#### **28. get_magento_products_by_category** ✅
```
CONVERSATION: "Show me category 123 products"
EXPECTED: Category-specific products
COMPONENT: Category Product Grid
```

---

### **🧠 MEMORY FUNCTIONS (POSTGRESQL + PGVECTOR - 2 Functions):**

#### **29. recall_user_memory** ✅
```
CONVERSATION: "Do you remember what I told you about my living room?"
EXPECTED: Memory retrieval + context
COMPONENT: Memory Recall Card
```

---

### **📞 COMMUNICATION FUNCTIONS (VAPI - 1 Function):**

#### **30. start_demo_call** ⚠️ (Need VAPI credentials)
```
CONVERSATION: "Call me at +1234567890"
EXPECTED: Real phone call initiation
COMPONENT: Call Status Card
```

---

## 🎬 **MEGA CONVERSATION TESTING SEQUENCE**

### **🔥 ULTIMATE LIVE TEST (15 minutes):**

```
=== PHASE 1: CUSTOMER IDENTIFICATION ===
👤 "My phone number is 407-288-6040"
Expected: Customer Profile Card

👤 "Show me my purchase history"  
Expected: Order History Card

👤 "Show me details for my order"
Expected: Order Details Card

=== PHASE 2: PRODUCT DISCOVERY ===
🛒 "What brands do you carry?"
Expected: Brand Grid (450+ brands)

🛒 "Show me Ashley sectionals"
Expected: Filtered Product Carousel

🛒 "What are your best sellers?"
Expected: Best Sellers Grid

🛒 "Show me recliners under $500"
Expected: Budget-filtered Products

🛒 "What colors are available?"
Expected: Color Palette Grid

=== PHASE 3: ADVANCED FEATURES ===
📊 "Analyze patterns for customer 9318667506"
Expected: Analytics Dashboard

💡 "What do you recommend for me?"
Expected: AI Recommendations Grid

🧠 "Do you remember what I told you before?"
Expected: Memory Recall

📷 "Show me photos of the second product"
Expected: Photo Gallery Carousel

=== PHASE 4: SUPPORT & COMMUNICATION ===
🚨 "I need help with a damaged delivery"
Expected: Support Ticket Creation

📞 "Call me at +13323339453"
Expected: Demo Call Initiation

🗺️ "How do I get to your Acworth store?"
Expected: Directions + Map

=== PHASE 5: CATEGORY BROWSING ===
🏠 "Show me dining room furniture"
Expected: Dining Product Grid

🛋️ "Show me all sectionals"
Expected: Sectional Collection

💺 "Show me all recliners"
Expected: Recliner Collection

=== PHASE 6: ADVANCED SEARCH ===
🔍 "Show me category 123 products"
Expected: Category-specific Products

🔍 "Tell me about SKU 1234567890"
Expected: Single Product Details

🔍 "What product categories do you have?"
Expected: Category Tree

=== PHASE 7: ADMIN FUNCTIONS (Admin Mode) ===
🔧 "Look up customer 407-288-6040"
Expected: Enhanced Customer Data

🔧 "Get customer journey for 407-288-6040"
Expected: Complete Journey Timeline

🔧 "Show customer analytics"
Expected: Advanced Analytics Dashboard
```

---

## 📊 **TESTING CHECKLIST**

### **✅ FUNCTION VERIFICATION:**
- [ ] **Customer Lookup** - Phone recognition works
- [ ] **Email Lookup** - Email recognition works  
- [ ] **Order History** - Orders display properly
- [ ] **Order Details** - Itemized breakdown works
- [ ] **Support Escalation** - Tickets created successfully
- [ ] **Product Search** - Magento products display
- [ ] **Brand Display** - 450+ brands shown
- [ ] **Color Options** - Color palette works
- [ ] **Price Filtering** - Budget search works
- [ ] **Photo Gallery** - SKU photos display
- [ ] **Best Sellers** - Featured products work
- [ ] **Memory Recall** - Long-term memory functions
- [ ] **Analytics** - Customer patterns display
- [ ] **Recommendations** - AI suggestions work
- [ ] **VAPI Calls** - Phone integration works
- [ ] **Store Directions** - Navigation help works

### **🎨 COMPONENT VERIFICATION:**
- [ ] **Customer Cards** - Profile displays beautifully
- [ ] **Order Cards** - History + details render
- [ ] **Product Carousels** - Products show in carousel
- [ ] **Photo Galleries** - Images display correctly
- [ ] **Analytics Dashboards** - Charts + stats render
- [ ] **Support Tickets** - Escalation cards work
- [ ] **Brand Grids** - Brand listings display
- [ ] **Memory Cards** - Recall results show

### **📱 RESPONSIVE TESTING:**
- [ ] **Desktop** - All functions work on desktop
- [ ] **Mobile** - Touch-friendly on mobile
- [ ] **Tablet** - Responsive on tablet sizes

---

## 🔧 **DEBUGGING COMMANDS**

### **Health Check:**
```javascript
fetch('https://woodstocknew-production.up.railway.app/health')
  .then(r => r.json())
  .then(console.log)
```

### **Direct Function Test:**
```javascript
fetch('https://woodstocknew-production.up.railway.app/v1/chat/completions', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    messages: [{"role": "user", "content": "My phone number is 407-288-6040"}]
  })
}).then(r => r.json()).then(console.log)
```

### **Console Logging:**
```javascript
// Watch for component rendering
console.log = function(originalLog) {
  return function(message) {
    if (message.includes('🎨') || message.includes('component')) {
      originalLog.apply(console, ['COMPONENT:', message]);
    }
    originalLog.apply(console, arguments);
  };
}(console.log);
```

---

## 🎯 **EXPECTED SUCCESS INDICATORS:**

### **✅ Backend Should Show:**
```
✅ nest-asyncio applied - TaskGroup errors fixed!
✅ MCP integration available
🔧 Initializing PydanticAI agent with memory...
✅ Agent initialized with 25+ ENHANCED functions
🚀 Starting LOFT Chat Backend with MEMORY...
```

### **✅ Frontend Should Show:**
```
🎨 WoodstockComponents initialized
🎨 Detected function result, rendering component for: get_customer_by_phone
🔍 Extracted data for customer profile
🎨 Component rendered successfully
```

### **✅ Health Check Should Return:**
```json
{
  "status": "ok",
  "message": "LOFT Chat Backend with Memory + MCP is running!",
  "model": "gpt-4.1",
  "native_functions": 30,
  "memory": "PostgreSQL (Existing Tables)"
}
```

---

## 🔄 **RAPID TESTING COMMANDS**

### **Quick Customer Test:**
```javascript
// Test customer lookup
woodstockChat.messageInput.value = "My phone is 407-288-6040"; 
woodstockChat.handleSubmit(new Event('submit'));
```

### **Quick Product Test:**
```javascript  
// Test product search
woodstockChat.messageInput.value = "Show me sectional sofas"; 
woodstockChat.handleSubmit(new Event('submit'));
```

### **Quick Support Test:**
```javascript
// Test support escalation
woodstockChat.messageInput.value = "I need help with a damaged delivery"; 
woodstockChat.handleSubmit(new Event('submit'));
```

### **Quick Memory Test:**
```javascript
// Test memory recall
woodstockChat.messageInput.value = "Do you remember what I told you?"; 
woodstockChat.handleSubmit(new Event('submit'));
```

---

## 📋 **RESULTS TRACKING TEMPLATE:**

```
FUNCTION TESTED: [Function Name]
CONVERSATION USED: "[Exact message]"
✅ WORKS / ❌ FAILS: 
COMPONENT RENDERED: ✅ YES / ❌ NO
CONSOLE ERRORS: [Copy any errors]
RESPONSE TIME: [Seconds]
NOTES: [Additional observations]

---
```

---

## 🔥 **COMPLETE 30-FUNCTION MARATHON TEST:**

**Copy and paste these one by one, record results:**

```
My phone number is 407-288-6040
Show me my order history  
Show me details for order 0710544II27
My email is jdan4sure@yahoo.com
Show my complete customer journey
Analyze patterns for customer 9318667506
What products do you recommend for me?
Show customer analytics for 407-288-6040
I just placed an order, any suggestions?
I need help with a damaged delivery
How is my loyalty status?
Based on my history, what should I buy?
I need to speak to someone
How do I get to your store in Acworth?
What brands do you carry?
What colors are available?
Show me recliners under $500
Show me Ashley sectionals  
Show me photos of SKU 1234567890
What are your best sellers?
Show me sectional sofas
Show me sectionals
Show me recliners
Show me dining room furniture
Tell me about product SKU 1234567890
What product categories do you have?
Look up Magento customer jdan4sure@yahoo.com
Show me category 123 products
Do you remember what I told you about my living room?
Call me at +13323339453
```

---

## 📊 **SUCCESS METRICS:**

### **Target Results:**
- **Functions Working:** 28/30 (93%+ success rate)
- **Components Rendering:** 25/30 (83%+ visual success)  
- **Response Time:** <3 seconds average
- **Mobile Responsive:** 100% touch-friendly
- **Error Recovery:** Graceful degradation

### **Critical Success Factors:**
- ✅ Customer recognition works perfectly
- ✅ Product search shows beautiful carousels
- ✅ Support escalation creates tickets
- ✅ Memory system recalls information
- ✅ All components render on mobile
- ✅ No JavaScript errors in console

---

## 🚀 **DEPLOYMENT STATUS VERIFICATION:**

**Copy this into browser console:**
```javascript
// Complete system health check
async function testEverything() {
  console.log('🔥 TESTING ALL WOODSTOCK FUNCTIONS');
  
  // 1. Health check
  const health = await fetch('/health').then(r => r.json());
  console.log('Health:', health);
  
  // 2. Test customer lookup
  const customerTest = await fetch('/v1/chat/completions', {
    method: 'POST', 
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      messages: [{"role": "user", "content": "My phone is 407-288-6040"}]
    })
  }).then(r => r.json());
  console.log('Customer:', customerTest);
  
  // 3. Test product search
  const productTest = await fetch('/v1/chat/completions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}, 
    body: JSON.stringify({
      messages: [{"role": "user", "content": "Show me sectionals"}]
    })
  }).then(r => r.json());
  console.log('Products:', productTest);
  
  console.log('🎯 ALL TESTS COMPLETE');
}

testEverything();
```

---

**🎯 NOW TEST EVERYTHING AND GIVE ME THE RESULTS!** 

**Copy each conversation example, test it live, and tell me:**
1. ✅ Function worked / ❌ Function failed
2. ✅ Component rendered / ❌ No component  
3. Any console errors
4. Response quality

**LET'S VERIFY ALL 30+ FUNCTIONS ARE WORKING! 🚀**
