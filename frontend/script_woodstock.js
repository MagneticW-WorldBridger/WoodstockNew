// Woodstock Outlet Chat - Dual Mode Implementation (Customer + Admin)
class WoodstockChat {
    constructor() {
        this.apiBase = (typeof window !== 'undefined' && window.BACKEND_URL) ? window.BACKEND_URL : 'http://localhost:8000';
        this.isConnected = false;
        this.isThinking = false;
        
        // Dual Mode Detection
        this.isAdminMode = this.detectAdminMode();
        this.isAuthenticated = false;
        this.customerData = null;
        
        // Session management
        this.sessionId = localStorage.getItem('woodstock-session') || this.generateSessionId();
        this.userIdentifier = localStorage.getItem('woodstock-user') || null;
        this.messageHistory = [];
        
        // DOM Elements
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.charCount = document.getElementById('charCount');
        
        this.init();
    }

    detectAdminMode() {
        // Check URL parameters for admin mode
        const urlParams = new URLSearchParams(window.location.search);
        const isAdmin = urlParams.get('admin') === 'true' || 
                       urlParams.get('mode') === 'admin' ||
                       window.location.hostname.includes('admin') ||
                       window.location.pathname.includes('/admin');
        
        console.log('🔧 Admin mode detected:', isAdmin);
        return isAdmin;
    }

    generateSessionId() {
        const prefix = this.isAdminMode ? 'admin_' : 'customer_';
        const id = prefix + Math.random().toString(36).substr(2, 16);
        localStorage.setItem('woodstock-session', id);
        console.log('🆔 Generated session ID:', id);
        return id;
    }

    detectUserIdentifier(message) {
        // Phone pattern
        const phoneMatch = message.match(/\b\d{3}-\d{3}-\d{4}\b/);
        if (phoneMatch && phoneMatch[0]) {
            this.userIdentifier = phoneMatch[0];
            localStorage.setItem('woodstock-user', this.userIdentifier);
            console.log('🔍 Auto-detected user:', this.userIdentifier);
            return this.userIdentifier;
        }
        
        // Email pattern  
        const emailMatch = message.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
        if (emailMatch && emailMatch[0]) {
            this.userIdentifier = emailMatch[0];
            localStorage.setItem('woodstock-user', this.userIdentifier);
            console.log('🔍 Auto-detected user:', this.userIdentifier);
            return this.userIdentifier;
        }
        
        return null;
    }

    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               window.innerWidth <= 768;
    }

    addMobileEventListeners() {
        // Handle viewport changes on mobile (keyboard show/hide)
        if (this.isMobile()) {
            let initialViewportHeight = window.innerHeight;
            
            window.addEventListener('resize', () => {
                const currentHeight = window.innerHeight;
                const heightDifference = initialViewportHeight - currentHeight;
                
                // If keyboard is likely open (significant height reduction)
                if (heightDifference > 150) {
                    document.body.classList.add('keyboard-open');
                } else {
                    document.body.classList.remove('keyboard-open');
                }
            });

            // Handle touch events for better mobile experience
            this.messageInput.addEventListener('touchstart', () => {
                // Scroll to input when touched on mobile
                setTimeout(() => {
                    this.messageInput.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }, 300);
            });

            // Prevent double-tap zoom on buttons
            this.sendButton.addEventListener('touchend', (e) => {
                e.preventDefault();
                this.sendButton.click();
            });
        }
    }

    init() {
        console.log('🚀 Initializing Woodstock Chat...');
        console.log('🎯 Mode:', this.isAdminMode ? 'ADMIN' : 'CUSTOMER');
        console.log('🆔 Session ID:', this.sessionId);
        console.log('👤 User Identifier:', this.userIdentifier);
        
        // Setup UI based on mode
        this.setupUI();
        
        // Event Listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResize());
        
        // Mobile-specific event listeners
        this.addMobileEventListeners();
        
        // Test connection
        this.testConnection();
        
        // Focus input (delayed for mobile)
        setTimeout(() => {
            if (!this.isMobile()) {
                this.messageInput.focus();
            }
        }, 500);
        
        console.log('✅ Woodstock Chat initialized!');
    }

    setupUI() {
        // Update UI based on mode
        if (this.isAdminMode) {
            this.setupAdminUI();
        } else {
            this.setupCustomerUI();
        }
    }

    setupAdminUI() {
        // Update header for admin mode
        const logoText = document.querySelector('.woodstock-logo-text');
        const subtitle = document.querySelector('.woodstock-subtitle');
        
        if (logoText) logoText.textContent = 'WOODSTOCK FURNITURE - ADMIN';
        if (subtitle) subtitle.textContent = 'Staff Dashboard';
        
        // Update welcome message for admin
        this.updateWelcomeMessage('admin');
        
        // Add admin indicator
        document.body.classList.add('admin-mode');
        
        console.log('🔧 Admin UI configured');
    }

    setupCustomerUI() {
        // Ensure customer UI is set up correctly
        const logoText = document.querySelector('.woodstock-logo-text');
        const subtitle = document.querySelector('.woodstock-subtitle');
        
        if (logoText) logoText.textContent = 'WOODSTOCK FURNITURE';
        if (subtitle) subtitle.textContent = 'AI Customer Support';
        
        // Update welcome message for customer
        this.updateWelcomeMessage('customer');
        
        // Add customer indicator
        document.body.classList.add('customer-mode');
        
        console.log('👤 Customer UI configured');
    }

    updateWelcomeMessage(mode) {
        const welcomeMsg = document.querySelector('.woodstock-message.assistant');
        if (!welcomeMsg) return;

        if (mode === 'admin') {
            welcomeMsg.innerHTML = `
                <h3>🔧 Admin Dashboard - All Functions Available</h3>
                <p>You have access to all 12 LOFT functions:</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div>
                        <strong>Customer Lookup:</strong><br>
                        • getCustomerByPhone<br>
                        • getCustomerByEmail<br><br>
                        <strong>Order Management:</strong><br>
                        • getOrdersByCustomer<br>
                        • getDetailsByOrder<br>
                    </div>
                    <div>
                        <strong>Analytics:</strong><br>
                        • analyzeCustomerPatterns<br>
                        • getCustomerAnalytics<br>
                        • getCustomerJourney<br><br>
                        <strong>Proactive Actions:</strong><br>
                        • All support & loyalty functions<br>
                    </div>
                </div>
                <p style="color: var(--woodstock-red); font-weight: 500;">
                    Try: "Look up customer 407-288-6040" or "Analyze patterns for customer 9318667506"
                </p>
            `;
        } else {
            welcomeMsg.innerHTML = `
                <h3>👋 Welcome to Woodstock Furniture Support</h3>
                <p>I'm your AI assistant, ready to help with:</p>
                <ul>
                    <li><strong>Order Status:</strong> Check your order progress</li>
                    <li><strong>Product Questions:</strong> Get recommendations</li>
                    <li><strong>Returns & Exchanges:</strong> Easy return process</li>
                    <li><strong>Store Information:</strong> Hours, locations, contact</li>
                </ul>
                <p style="margin-top: 1rem; color: var(--woodstock-red); font-weight: 500;">
                    Try: "Check my order status" or "I need help with a return"
                </p>
            `;
        }
    }

    async testConnection() {
        try {
            console.log('🔧 Testing backend connection...');
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            if (data.status === 'ok') {
                this.setConnected(true);
                console.log('✅ Backend connected successfully!');
                console.log(`📱 Model: ${data.model}`);
                console.log(`🔧 Functions: ${data.functions} LOFT functions loaded`);
            } else {
                throw new Error('Health check failed');
            }
        } catch (error) {
            console.error('❌ Backend connection failed:', error);
            this.setConnected(false);
            this.showError('Cannot connect to backend. Please check if server is running on port 8001.');
        }
    }

    setConnected(connected) {
        this.isConnected = connected;
        
        if (connected) {
            this.statusDot.classList.add('connected');
            this.statusText.textContent = 'Connected';
            this.sendButton.disabled = false;
        } else {
            this.statusDot.classList.remove('connected');
            this.statusText.textContent = 'Disconnected';
            this.sendButton.disabled = true;
        }
    }

    setThinking(thinking) {
        this.isThinking = thinking;
        
        if (thinking) {
            this.statusText.textContent = 'AI is thinking...';
            this.sendButton.disabled = true;
        } else {
            this.statusText.textContent = 'Connected';
            this.sendButton.disabled = !this.isConnected;
        }
    }

    handleInputChange() {
        const length = this.messageInput.value.length;
        this.charCount.textContent = `${length}/1000`;
        
        // Enable/disable send button
        const hasText = length > 0;
        this.sendButton.disabled = !hasText || !this.isConnected || this.isThinking;
        
        // Warning for character count
        if (length > 900) {
            this.charCount.classList.add('warning');
        } else {
            this.charCount.classList.remove('warning');
        }
    }

    handleKeyDown(e) {
        // Send on Enter (but not Shift+Enter)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!this.sendButton.disabled) {
                this.handleSubmit(e);
            }
        }
    }

    autoResize() {
        const textarea = this.messageInput;
        // Reset height to auto to get the correct scrollHeight
        textarea.style.height = 'auto';
        
        // Calculate new height with mobile-friendly limits
        const maxHeight = this.isMobile() ? 100 : 120;
        const newHeight = Math.min(textarea.scrollHeight, maxHeight);
        
        textarea.style.height = newHeight + 'px';
        
        // Scroll to bottom if on mobile and textarea is focused
        if (this.isMobile() && document.activeElement === textarea) {
            setTimeout(() => {
                textarea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const message = this.messageInput.value.trim();
        if (!message || this.isThinking || !this.isConnected) return;

        console.log('📤 Sending message:', message);
        
        // Auto-detect user identifier
        const detectedUser = this.detectUserIdentifier(message);
        if (detectedUser) {
            console.log('👤 User identified:', detectedUser);
        }
        
        // Add user message to history
        this.messageHistory.push({ role: 'user', content: message });
        
        // Add user message to UI
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.handleInputChange();
        
        // Show thinking state
        this.setThinking(true);
        this.showTypingIndicator();
        
        try {
            await this.sendToAI(message);
        } catch (error) {
            console.error('❌ Send error:', error);
            this.showError('Failed to send message. Please try again.');
        } finally {
            this.setThinking(false);
            this.hideTypingIndicator();
        }
    }

    async sendToAI(message) {
        console.log('🤖 Sending to AI backend...');
        
        const requestBody = {
            messages: this.messageHistory.slice(-10), // Send last 10 messages for context
            stream: true,
            session_id: this.sessionId,
            user_identifier: this.userIdentifier,
            user_type: this.isAdminMode ? 'admin' : 'customer',
            admin_mode: this.isAdminMode
        };

        const response = await fetch(`${this.apiBase}/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        console.log('📡 Streaming response...');
        await this.handleStreamingResponse(response);
    }

    async handleStreamingResponse(response) {
        this.hideTypingIndicator();
        
        const messageDiv = this.addMessage('', 'assistant');
        const contentDiv = messageDiv.querySelector('.message-content');
        
        let fullResponse = '';
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n').filter(line => line.trim() !== '');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6).trim();
                        
                        if (data === '[DONE]') {
                            console.log('✅ Streaming completed');
                            // Format final response as HTML
                            if (fullResponse.trim()) {
                                contentDiv.innerHTML = this.formatAsHTML(fullResponse);
                                this.messageHistory.push({ role: 'assistant', content: fullResponse });
                                console.log('💾 Added assistant response to history');
                            }
                            return;
                        }

                        try {
                            const parsed = JSON.parse(data);
                            const delta = parsed.choices?.[0]?.delta;
                            
                            if (delta?.content) {
                                // Accumulate delta text
                                                            fullResponse += delta.content;
                            
                            // Check if response contains function call indicators
                            this.detectAndRenderComponents(fullResponse, contentDiv);
                            this.scrollToBottom();
                            }
                            
                        } catch (parseError) {
                            console.log('⚠️ Parse error (skipping):', parseError.message);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('❌ Streaming error:', error);
            this.showError('Connection lost while receiving response.');
        }
    }

    detectAndRenderComponents(fullResponse, contentDiv) {
        // Check if this response contains function call results
        const functionPatterns = [
            { pattern: /(?:found|located|here.*profile|customer.*profile)/i, func: 'getCustomerByPhone', trigger: /Name:\s*([^\n]+)|Phone:\s*([^\n]+)|Email:\s*([^\n]+)/i },
            { pattern: /order.*details|itemized|breakdown.*order/i, func: 'getDetailsByOrder', trigger: /Order.*ID:\s*([A-Z0-9]+)|Total:\s*\$[\d,]+/i },
            { pattern: /order.*history|orders.*found|orders.*customer/i, func: 'getOrdersByCustomer', trigger: /Order.*#\s*[A-Z0-9]+|Status:.*[A-Za-z]+/i },
            { pattern: /customer.*patterns|analytics|spending|total.*spent/i, func: 'analyzeCustomerPatterns', trigger: /Total.*Spent:\s*\$[\d,]+|favorite.*categories/i },
            { pattern: /customer.*journey|complete.*profile|order.*history/i, func: 'getCustomerJourney', trigger: /Customer.*journey|timeline|history/i },
            { pattern: /appointment.*scheduled|calendar.*event|meeting.*created/i, func: 'google_calendar-create-event', trigger: /appointment.*scheduled|event.*created/i }
        ];

        let detectedFunction = null;
        let shouldRenderComponent = false;

        // Check each pattern
        for (const { pattern, func, trigger } of functionPatterns) {
            if (pattern.test(fullResponse) && trigger.test(fullResponse)) {
                detectedFunction = func;
                shouldRenderComponent = true;
                break;
            }
        }

        if (shouldRenderComponent && detectedFunction && window.woodstockComponents) {
            try {
                console.log('🎨 Detected function result, rendering component for:', detectedFunction);
                
                // Extract structured data from response
                const componentData = this.extractDataFromResponse(fullResponse, detectedFunction);
                
                // Render component
                const componentHTML = window.woodstockComponents.renderFunctionResult(detectedFunction, componentData);
                contentDiv.innerHTML = componentHTML;
                
                return; // Exit early, component rendered
            } catch (error) {
                console.error('❌ Component rendering failed:', error);
                // Fall through to regular text formatting
            }
        }

        // Regular text formatting if no component detected
        contentDiv.innerHTML = this.formatAsHTML(fullResponse);
    }

    extractDataFromResponse(text, functionName) {
        // Extract structured data from text response based on function type
        const data = { data: { entry: [] } };

        if (functionName === 'getCustomerByPhone' || functionName === 'getCustomerByEmail') {
            // Extract customer data
            const nameMatch = text.match(/Name:\s*([^\n]+)/i);
            const phoneMatch = text.match(/Phone:\s*([^\n]+)/i);
            const emailMatch = text.match(/Email:\s*([^\n]+)/i);
            const addressMatch = text.match(/Address:\s*([^\n]+)/i);
            const customerIdMatch = text.match(/Customer ID:\s*([^\n]+)/i);

            if (nameMatch || phoneMatch || emailMatch) {
                const nameParts = nameMatch ? nameMatch[1].split(' ') : ['', ''];
                data.data.entry = [{
                    firstname: nameParts[0] || '',
                    lastname: nameParts.slice(1).join(' ') || '',
                    phonenumber: phoneMatch ? phoneMatch[1].trim() : '',
                    email: emailMatch ? emailMatch[1].trim() : '',
                    address: addressMatch ? addressMatch[1].trim() : '',
                    customerid: customerIdMatch ? customerIdMatch[1].trim() : ''
                }];
            }
        }

        else if (functionName === 'getDetailsByOrder') {
            // Extract order details
            const items = [];
            const itemMatches = text.match(/([^\n]+):\s*\$([0-9,.]+)/g);
            
            if (itemMatches) {
                itemMatches.forEach(match => {
                    const parts = match.split(':');
                    if (parts.length === 2) {
                        const description = parts[0].trim();
                        const price = parts[1].replace('$', '').trim();
                        items.push({
                            description,
                            itemprice: price,
                            qtyordered: '1',
                            productid: 'N/A'
                        });
                    }
                });
            }

            data.data.entry = items;
        }

        else if (functionName === 'getOrdersByCustomer') {
            // Extract orders list
            const orderMatches = text.match(/Order.*#?\s*([A-Z0-9]+)[^\n]*\$([0-9,.]+)/gi);
            const orders = [];

            if (orderMatches) {
                orderMatches.forEach(match => {
                    const idMatch = match.match(/([A-Z0-9]+)/);
                    const priceMatch = match.match(/\$([0-9,.]+)/);
                    
                    if (idMatch && priceMatch) {
                        orders.push({
                            orderid: idMatch[1],
                            ordertotal: priceMatch[1],
                            status: 'F', // Assume finalized
                            orderdate: new Date().toISOString()
                        });
                    }
                });
            }

            data.data.entry = orders;
        }

        else if (functionName === 'analyzeCustomerPatterns') {
            // Extract analytics data
            const totalSpentMatch = text.match(/\$([0-9,.]+)/);
            const orderCountMatch = text.match(/(\d+)\s*orders?/i);
            
            data.data = {
                totalSpent: totalSpentMatch ? totalSpentMatch[1] : '0',
                orderCount: orderCountMatch ? parseInt(orderCountMatch[1]) : 0,
                favoriteCategories: [
                    { category: 'Sectionals', count: 1 },
                    { category: 'Recliners', count: 1 }
                ]
            };
        }

        console.log('🔍 Extracted data for', functionName, ':', data);
        return data;
    }

    formatAsHTML(text, functionName = null, functionData = null) {
        // Check if this is a function result that should use amazing components
        if (functionName && functionData && window.woodstockComponents) {
            try {
                console.log('🎨 Using amazing components for:', functionName);
                return window.woodstockComponents.renderFunctionResult(functionName, functionData);
            } catch (error) {
                console.error('❌ Component rendering failed, falling back to text:', error);
                // Fall through to text formatting
            }
        }

        // Convert Woodstock-style responses to clean HTML
        let html = text;
        
        // Convert markdown-style formatting to HTML
        html = html
            .replace(/\*\*\*(.+?)\*\*\*/g, '<strong style="color: var(--woodstock-red);">$1</strong>')
            .replace(/\*\*(.+?)\*\*/g, '<strong style="color: var(--woodstock-navy);">$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/`(.+?)`/g, '<code style="background: rgba(0,33,71,0.1); padding: 2px 4px; border-radius: 3px;">$1</code>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        // Wrap in paragraph if not already structured
        if (!html.includes('<')) {
            html = `<p>${html}</p>`;
        }
        
        // Style customer data
        html = html.replace(/(Customer ID: )(\d+)/g, '$1<span class="highlight">$2</span>');
        html = html.replace(/(Order ID: )([A-Z0-9]+)/g, '$1<span class="highlight">$2</span>');
        html = html.replace(/(\$[\d,]+\.?\d*)/g, '<span class="price-tag">$1</span>');
        
        return html;
    }

    addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `woodstock-message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (role === 'assistant') {
            contentDiv.innerHTML = content ? this.formatAsHTML(content) : '';
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);
        
        // Mobile-friendly scroll to bottom
        this.scrollToBottom();
        return messageDiv;
    }

    showTypingIndicator() {
        const existingIndicator = document.querySelector('.woodstock-typing');
        if (existingIndicator) return;
        
        const indicator = document.createElement('div');
        indicator.className = 'woodstock-typing';
        indicator.innerHTML = `
            <span style="color: var(--woodstock-navy); font-weight: 500;">AI is thinking</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.messagesContainer.appendChild(indicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const indicator = document.querySelector('.woodstock-typing');
        if (indicator) {
            indicator.remove();
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'woodstock-message assistant';
        errorDiv.innerHTML = `
            <div class="error-message">
                <strong>Error:</strong> ${message}
            </div>
        `;
        
        this.messagesContainer.appendChild(errorDiv);
        this.scrollToBottom();
    }

    scrollToBottom() {
        requestAnimationFrame(() => {
            const container = this.messagesContainer;
            const scrollOptions = {
                top: container.scrollHeight,
                behavior: 'smooth'
            };
            
            // Use smooth scrolling for better mobile experience
            if (container.scrollTo) {
                container.scrollTo(scrollOptions);
            } else {
                // Fallback for older browsers
                container.scrollTop = container.scrollHeight;
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOM loaded, initializing Woodstock Chat...');
    
    const chat = new WoodstockChat();
    
    console.log('🔧 Woodstock Chat ready!');
    console.log('📱 Backend API:', chat.apiBase);
    console.log('🌐 Frontend URL:', window.location.href);
    
    // Global access for debugging
    window.woodstockChat = chat;
});

// 12 ENDPOINT TESTING COMMANDS FOR CONSOLE:
console.log(`
🧪 WOODSTOCK CHAT - 12 ENDPOINT TESTS:

// CORE API (4):
woodstockChat.messageInput.value = "Find customer with phone 407-288-6040"; woodstockChat.handleSubmit(new Event('submit'));
woodstockChat.messageInput.value = "Find customer with email jdan4sure@yahoo.com"; woodstockChat.handleSubmit(new Event('submit'));
woodstockChat.messageInput.value = "Get orders for customer 9318667506"; woodstockChat.handleSubmit(new Event('submit'));
woodstockChat.messageInput.value = "Show details for order 0710544II27"; woodstockChat.handleSubmit(new Event('submit'));

// ANALYSIS (2):
woodstockChat.messageInput.value = "Analyze purchase patterns for customer 9318667506"; woodstockChat.handleSubmit(new Event('submit'));
woodstockChat.messageInput.value = "Give product recommendations for customer 9318667506"; woodstockChat.handleSubmit(new Event('submit'));

// PROACTIVE (4):
woodstockChat.messageInput.value = "Confirm order and cross-sell for 407-288-6040"; woodstockChat.handleSubmit(new Event('submit'));
woodstockChat.messageInput.value = "Escalate support issue for 407-288-6040: delivery damaged"; woodstockChat.handleSubmit(new Event('submit'));
woodstockChat.messageInput.value = "Check loyalty upgrade for 407-288-6040"; woodstockChat.handleSubmit(new Event('submit'));
woodstockChat.messageInput.value = "Generate personalized recommendations for 407-288-6040"; woodstockChat.handleSubmit(new Event('submit'));

// COMPOSITE (2):
woodstockChat.messageInput.value = "Get complete customer journey for 407-288-6040"; woodstockChat.handleSubmit(new Event('submit'));
woodstockChat.messageInput.value = "Give comprehensive analytics for 407-288-6040"; woodstockChat.handleSubmit(new Event('submit'));
`);

console.log('📁 Woodstock Chat script loaded successfully!');
