# 🔐 URL PARAMETER AUTHENTICATION - TESTING GUIDE

## **How to Test URL Authentication**

The system now supports passing authentication parameters via the API request body. Here's how to test it:

---

## 📝 **METHOD 1: Using curl (Terminal)**

### **Test with customer_id:**
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "what are my orders?"}
    ],
    "customer_id": "9318667498",
    "auth_level": "authenticated"
  }'
```

### **Test with loft_id:**
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "show my order history"}
    ],
    "loft_id": "ABC12345",
    "auth_level": "authenticated"
  }'
```

### **Test with email:**
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "my order status"}
    ],
    "email": "selenebarcia448@gmail.com",
    "auth_level": "authenticated"
  }'
```

---

## 📝 **METHOD 2: Using Postman**

1. **Open Postman**
2. **Create new POST request:** `http://localhost:8001/v1/chat/completions`
3. **Headers:**
   - Content-Type: `application/json`
4. **Body (raw JSON):**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "what are my orders?"
    }
  ],
  "customer_id": "9318667498",
  "loft_id": "ABC123",
  "email": "selenebarcia448@gmail.com",
  "auth_level": "authenticated"
}
```

5. **Send** and check logs

---

## 📝 **METHOD 3: Frontend Integration**

### **Modify frontend to include auth params:**

```javascript
// In script_woodstock.js, modify sendMessage function:

async sendMessage(userMessage) {
    // ... existing code ...
    
    const payload = {
        messages: messages,
        stream: true,
        model: "loft-chat",
        
        // ADD THESE LINES:
        customer_id: "9318667498",  // Get from URL params or session
        loft_id: "ABC123",          // Get from URL params
        email: "user@example.com",   // Get from URL params
        auth_level: "authenticated"  // Set based on URL presence
    };
    
    // ... rest of code ...
}
```

### **Get from URL parameters:**
```javascript
// Add at top of script_woodstock.js:

function getURLAuthParams() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
        customer_id: urlParams.get('customer_id'),
        loft_id: urlParams.get('loft_id'),
        email: urlParams.get('email'),
        auth_level: urlParams.get('customer_id') || urlParams.get('loft_id') || urlParams.get('email') 
            ? 'authenticated' 
            : 'anonymous'
    };
}

// Use in sendMessage:
const authParams = getURLAuthParams();
const payload = {
    messages: messages,
    stream: true,
    model: "loft-chat",
    ...authParams  // Spread auth params
};
```

### **Test URL:**
```
http://localhost:8001/frontend/index.html?customer_id=9318667498&loft_id=ABC123&email=selenebarcia448@gmail.com
```

---

## ✅ **EXPECTED RESULTS**

### **In Backend Logs:**
```
👤 UserContext created: 9318667498 (level: authenticated)
💾 Stored user context for conversation abc123
🔐 Auth level: authenticated (customer_id=9318667498, loft_id=ABC123)
```

### **In Response:**
- System automatically uses customer_id for API calls
- Personalized responses based on customer data
- No need to ask "what's your phone number?"
- Direct order lookups without authentication prompts

---

## 🧪 **VERIFICATION STEPS**

### **1. Check Context Creation:**
```bash
# In terminal where server is running, look for:
👤 UserContext created: [identifier] (level: authenticated)
```

### **2. Check Auto-Authentication:**
```bash
# User asks: "what are my orders?"
# System should call: get_orders_by_customer(customer_id="9318667498")
# WITHOUT asking for phone number first
```

### **3. Check Personalization:**
```bash
# Response should include:
- User's actual name
- User's order history
- Personalized recommendations
```

---

## 🐛 **TROUBLESHOOTING**

### **Issue: "UserContext not created"**
**Check:**
1. Request includes auth fields in body
2. Fields are at top level (not nested in messages)
3. Spelling: `customer_id` not `customerId`

### **Issue: "Auth level stays anonymous"**
**Check:**
1. At least one of: customer_id, loft_id, or email is provided
2. Values are not null or empty strings
3. auth_level parameter is optional (auto-detected)

### **Issue: "System still asks for phone"**
**Check:**
1. UserContext was stored (check logs for "💾 Stored user context")
2. conversation_id is being passed correctly
3. Context hasn't expired (check conversation_id matches)

---

## 🎯 **USE CASES**

### **1. Embedded Chat Widget:**
```javascript
// When user logs into your site:
const chatWidget = {
    customer_id: currentUser.id,
    loft_id: currentUser.loft_id,
    email: currentUser.email
};

// All subsequent chats use these credentials automatically
```

### **2. Email Link:**
```
https://yoursite.com/chat?customer_id=12345&email=user@example.com

// User clicks from email → Chat opens authenticated
// No login required, immediate personalized experience
```

### **3. Admin Dashboard:**
```javascript
// Admin viewing customer account:
const chatContext = {
    customer_id: selectedCustomer.id,
    auth_level: "admin"  // Admin can view any customer
};

// Chat opens with full customer context
// Admin sees complete history instantly
```

---

## 📊 **EXPECTED BEHAVIOR**

| Scenario | customer_id | loft_id | email | auth_level | Result |
|----------|-------------|---------|-------|------------|--------|
| Anonymous | ❌ | ❌ | ❌ | anonymous | Generic experience |
| URL Params | ✅ | ✅ | ✅ | authenticated | Full personalization |
| Customer ID only | ✅ | ❌ | ❌ | authenticated | Uses customer_id |
| Email only | ❌ | ❌ | ✅ | authenticated | Uses email |
| Admin override | ✅ | ❌ | ❌ | admin | Admin privileges |

---

## 🚀 **INTEGRATION EXAMPLE**

### **Complete Frontend Integration:**

```javascript
// At page load:
const urlParams = new URLSearchParams(window.location.search);
const authContext = {
    customer_id: urlParams.get('customer_id'),
    loft_id: urlParams.get('loft_id'),
    email: urlParams.get('email')
};

// Store globally:
window.woodstockAuth = authContext;

// In sendMessage function:
async sendMessage(userMessage) {
    const payload = {
        messages: [...],
        stream: true,
        ...window.woodstockAuth  // Include auth automatically
    };
    
    const response = await fetch('/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
}
```

---

## 📝 **QUICK TEST SCRIPT**

Save as `test_auth.sh`:

```bash
#!/bin/bash

echo "🔐 Testing URL Parameter Authentication..."
echo ""

# Test 1: customer_id
echo "Test 1: customer_id authentication"
curl -s -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "my orders"}],
    "customer_id": "9318667498"
  }' | jq .

echo ""
echo "---"
echo ""

# Test 2: email
echo "Test 2: email authentication"
curl -s -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "my account"}],
    "email": "selenebarcia448@gmail.com"
  }' | jq .

echo ""
echo "✅ Tests complete - check backend logs for UserContext creation"
```

Run: `chmod +x test_auth.sh && ./test_auth.sh`

---

**Status:** ✅ Ready for testing
**Documentation:** Complete
**Integration:** Simple - just add fields to request body

