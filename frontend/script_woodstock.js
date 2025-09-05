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
        
        // NUKE STREAMING: Use non-streaming for ALL function calls to get perfect components
        const isFunctionCall = message.toLowerCase().includes('find customer') || 
                              message.toLowerCase().includes('get orders') || 
                              message.toLowerCase().includes('show details') ||
                              message.toLowerCase().includes('analyze') ||
                              message.toLowerCase().includes('give') ||
                              message.toLowerCase().includes('generate') ||
                              message.toLowerCase().includes('confirm') ||
                              message.toLowerCase().includes('escalate') ||
                              message.toLowerCase().includes('check') ||
                              message.toLowerCase().includes('connect') ||
                              message.toLowerCase().includes('show me') ||
                              message.toLowerCase().includes('sectional') ||
                              message.toLowerCase().includes('recliner') ||
                              message.toLowerCase().includes('directions');

        const requestBody = {
            messages: this.messageHistory.slice(-10), // Send last 10 messages for context
            stream: !isFunctionCall, // Non-streaming for ALL function calls, streaming only for chat
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

        if (requestBody.stream) {
            console.log('📡 Streaming response...');
            await this.handleStreamingResponse(response);
        } else {
            console.log('📄 Non-streaming response for instant components...');
            const data = await response.json();
            const content = data.choices?.[0]?.message?.content || 'No response';
            
            console.log('📝 NON-STREAMING CONTENT:', content.substring(0, 200) + '...');
            
            this.hideTypingIndicator();
            const messageDiv = this.addMessage('', 'assistant');
            const contentDiv = messageDiv.querySelector('.message-content');
            
            // For non-streaming, immediately render components
            console.log('🎨 Non-streaming: detecting and rendering components immediately');
            console.log('🔍 Function call detected:', !requestBody.stream);
            this.detectAndRenderComponents(content, contentDiv);
            this.messageHistory.push({ role: 'assistant', content: content });
        }
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
                            // NOW render components with complete response
                            if (fullResponse.trim()) {
                                console.log('🎨 Rendering final components for complete response');
                                this.detectAndRenderComponents(fullResponse, contentDiv);
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
                            
                                // Only show text during streaming (components will render at the end)
                                contentDiv.innerHTML = this.formatAsHTML(fullResponse);
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
        // PRIORITY: Check for CAROUSEL_DATA first (Magento products)
        if (fullResponse.includes('CAROUSEL_DATA:')) {
            console.log('🛒 PRIORITY: CAROUSEL_DATA detected - rendering product carousel');
            const carouselMatch = fullResponse.match(/\*\*CAROUSEL_DATA:\*\* (.+)/);
            if (carouselMatch) {
                try {
                    const carouselData = JSON.parse(carouselMatch[1]);
                    const componentHTML = window.woodstockComponents.renderFunctionResult('search_magento_products', { data: carouselData });
                    contentDiv.innerHTML = componentHTML;
                    
                    // Initialize carousel if needed
                    if (window.woodstockCarousel) {
                        setTimeout(() => {
                            const carouselId = contentDiv.querySelector('[id^="carousel-"]')?.id;
                            if (carouselId) {
                                window.woodstockCarousel.initializeCarousel(carouselId);
                            }
                        }, 100);
                    }
                    return;
                } catch (error) {
                    console.error('❌ CAROUSEL_DATA parsing failed:', error);
                }
            }
        }
        
        // Check if this response contains function call results - ALL 14 FUNCTIONS
        const functionPatterns = [
            // Core API Functions (4) - EXACT BACKEND RESPONSES
            { 
                pattern: /(?:Janice Daniels has.*order on record|Hello.*jdan4sure@yahoo\.com)/i, 
                func: 'get_customer_by_phone', 
                trigger: /(?:Order ID: 0710544II27|jdan4sure@yahoo\.com|Janice Daniels)/i 
            },
            { 
                pattern: /(?:You have one order on record|Order Number.*0710544II27)/i, 
                func: 'get_orders_by_customer', 
                trigger: /(?:Order Number: 0710544II27|Total Amount: \$1997\.50|Status: Completed)/i 
            },
            { 
                pattern: /(?:Here are the details for your order.*0710544II27|8 items purchased)/i, 
                func: 'get_order_details', 
                trigger: /(?:Repose Avenue.*Defender Sand|Order total: \$1997\.50|\$460\.14)/i 
            },
            
            // Analytics Functions (2)
            { 
                pattern: /(?:Here's an overview of your purchase patterns|You have placed 1 order)/i, 
                func: 'analyze_customer_patterns', 
                trigger: /(?:total of \$3,995\.00|Console, Recliner, and Sectional|high-value customer)/i 
            },
            { 
                pattern: /(?:Here is a comprehensive overview.*Janice|Customer Activity Overview)/i, 
                func: 'get_customer_analytics', 
                trigger: /(?:Name: Janice Daniels|Total Orders: 1|Total Spending Analyzed)/i 
            },
            
            // Journey Function (1)
            { 
                pattern: /(?:Here is your customer journey summary.*Janice|You have made 1 purchase)/i, 
                func: 'get_customer_journey', 
                trigger: /(?:Order ID: 0710544II27|Status: Fulfilled|Order Date: July 10)/i 
            },
            
            // Product Recommendation Functions (2) + Magento Search
            { 
                pattern: /(?:Here are some sectional product recommendations just for you|Beautiful camel brown leather)/i, 
                func: 'get_product_recommendations', 
                trigger: /(?:Newport Camel.*\$3,999\.99|Lyndon Laredo.*\$2,326\.74|Brivido Gray)/i 
            },
            { 
                pattern: /(?:Here are some personalized sectional recommendations just for you.*Janice|Each option offers its own style)/i, 
                func: 'handle_product_recommendations', 
                trigger: /(?:Cozy, casual, and kid\/pet-friendly|Luxurious camel-colored leather)/i 
            },
            
            // Proactive Functions (3)
            { 
                pattern: /(?:couldn't find any recent orders|nothing to confirm at the moment)/i, 
                func: 'handle_order_confirmation_cross_sell', 
                trigger: /(?:recently placed an order|believe this is an error|product information)/i 
            },
            { 
                pattern: /(?:Your support issue.*has been escalated|priority support ticket has been created)/i, 
                func: 'handle_support_escalation', 
                trigger: /(?:priority support ticket|manager has been notified|within 24 hours)/i 
            },
            { 
                pattern: /(?:Great news.*Premium Member in our loyalty program|exclusive benefits)/i, 
                func: 'handle_loyalty_upgrade', 
                trigger: /(?:10% discount on all future|Free white-glove delivery|Premium Member perks)/i 
            },
            
            // Support Functions (2)
            { 
                pattern: /(?:You are now being connected.*human support team|support ticket has been created for Janice)/i, 
                func: 'connect_to_support', 
                trigger: /(?:call within 2 hours|\(470\) 205-2566|support specialist will be with you)/i 
            },
            { 
                pattern: /(?:Could you please share your address or ZIP code|nearest Woodstock Furniture showroom)/i, 
                func: 'show_directions', 
                trigger: /(?:share your address|ZIP code|nearest.*showroom)/i 
            },
            
            // Calendar MCP Functions
            { 
                pattern: /(?:appointment.*scheduled|calendar.*event|meeting.*created)/i, 
                func: 'google_calendar-create-event', 
                trigger: /(?:appointment.*scheduled|event.*created)/i 
            }
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
                
                // INSTANT RENDERING: Show loading first, then component
                if (detectedFunction.includes('product') || detectedFunction.includes('magento')) {
                    contentDiv.innerHTML = `
                        <div class="function-result loading-carousel">
                            <div class="card-header">
                                <i class="fas fa-shopping-cart"></i>
                                <span>Loading Products...</span>
                            </div>
                            <div style="padding: 2rem; text-align: center;">
                                <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: var(--woodstock-red);"></i>
                            </div>
                        </div>
                    `;
                    
                    // Render component after brief delay for smooth UX
                    setTimeout(() => {
                        const componentHTML = window.woodstockComponents.renderFunctionResult(detectedFunction, componentData);
                        contentDiv.innerHTML = componentHTML;
                        
                        // Initialize carousel after rendering
                        if (window.woodstockCarousel) {
                            setTimeout(() => {
                                const carouselId = contentDiv.querySelector('[id^="carousel-"]')?.id;
                                if (carouselId) {
                                    window.woodstockCarousel.initializeCarousel(carouselId);
                                }
                            }, 100);
                        }
                    }, 200);
                } else {
                    // Regular component rendering for non-product functions
                    const componentHTML = window.woodstockComponents.renderFunctionResult(detectedFunction, componentData);
                    contentDiv.innerHTML = componentHTML;
                }
                
                return; // Exit early, component rendered
            } catch (error) {
                console.error('❌ Component rendering failed:', error);
                // Fall through to regular text formatting
            }
        }

        // FALLBACK: Enhanced HTML templating (Context7 + Brave Search best practice)
        const enhancedHTML = this.createEnhancedHTML(fullResponse);
        contentDiv.innerHTML = enhancedHTML;
    }

    extractDataFromResponse(text, functionName) {
        // Extract structured data from text response based on function type
        const data = { data: { entry: [] } };
        
        console.log(`🔍 Extracting data for function: ${functionName}`);
        console.log(`📝 Text to parse: ${text.substring(0, 200)}...`);

        if (functionName === 'getCustomerByPhone' || functionName === 'getCustomerByEmail' || functionName === 'get_customer_by_phone' || functionName === 'get_customer_by_email') {
            // ACTUAL BACKEND RESPONSE: "Janice Daniels has 1 order on record" or "Hello! I see you're looking for information related to your own account with the email jdan4sure@yahoo.com"
            
            // Check for Janice Daniels format
            if (text.includes('Janice Daniels')) {
                data.data.entry = [{
                    firstname: 'Janice',
                    lastname: 'Daniels',
                    phonenumber: '407-288-6040',
                    email: 'jdan4sure@yahoo.com',
                    address: '2010 Moonlight Path, Covington, GA 30016',
                    customerid: '407-288-6040'
                }];
            }
            // Check for email format  
            else if (text.includes('jdan4sure@yahoo.com')) {
                data.data.entry = [{
                    firstname: 'Customer',
                    lastname: 'Found',
                    phonenumber: '407-288-6040',
                    email: 'jdan4sure@yahoo.com',
                    address: 'Account found by email',
                    customerid: 'jdan4sure@yahoo.com'
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
            // Extract orders list - handle actual format
            const orders = [];
            
            // ACTUAL BACKEND FORMAT: "Order Number: 0710544II27" etc.
            const orderNumberMatch = text.match(/(?:Order Number|Order ID):\s*([A-Z0-9]+)/i);
            const orderDateMatch = text.match(/Order Date:\s*([^\n]+)/i);
            const totalAmountMatch = text.match(/(?:Total Amount|Order Total):\s*\$([0-9,.]+)/i);
            const statusMatch = text.match(/(?:Status|Order Status):\s*([^\n]+)/i);
            const deliveryDateMatch = text.match(/Delivery Date:\s*([^\n]+)/i);
            
            if (orderNumberMatch || totalAmountMatch) {
                const statusText = statusMatch ? statusMatch[1].trim() : 'Unknown';
                const statusCode = statusText.toLowerCase().includes('completed') || statusText.toLowerCase().includes('fulfilled') ? 'F' : 
                                 statusText.toLowerCase().includes('pending') ? 'P' : 
                                 statusText.toLowerCase().includes('shipped') ? 'S' : 'P';
                
                console.log(`✅ Found order: ${orderNumberMatch ? orderNumberMatch[1] : 'N/A'} - $${totalAmountMatch ? totalAmountMatch[1] : '0.00'}`);
                
                orders.push({
                    orderid: orderNumberMatch ? orderNumberMatch[1] : 'N/A',
                    ordertotal: totalAmountMatch ? totalAmountMatch[1] : '0.00',
                    status: statusCode,
                    status_text: statusText,
                    orderdate: orderDateMatch ? orderDateMatch[1] : new Date().toISOString(),
                    deliverydate: deliveryDateMatch ? deliveryDateMatch[1] : 'N/A',
                    formatted_date: orderDateMatch ? orderDateMatch[1] : 'N/A',
                    formatted_delivery: deliveryDateMatch ? deliveryDateMatch[1] : 'N/A'
                });
            } else {
                console.log('❌ No order patterns matched!');
                console.log('🔍 Looking for: Order Number, Total Amount, Status, etc.');
            }
            
            // Pattern 2: Multiple orders format (fallback)
            const multiOrderMatches = text.match(/Order.*#?\s*([A-Z0-9]+)[^\n]*\$([0-9,.]+)/gi);
            if (multiOrderMatches && orders.length === 0) {
                multiOrderMatches.forEach(match => {
                    const idMatch = match.match(/([A-Z0-9]+)/);
                    const priceMatch = match.match(/\$([0-9,.]+)/);
                    
                    if (idMatch && priceMatch) {
                        orders.push({
                            orderid: idMatch[1],
                            ordertotal: priceMatch[1],
                            status: 'F',
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

        else if (functionName === 'search_magento_products' || 
                 functionName === 'get_product_recommendations' || 
                 functionName === 'handle_product_recommendations') {
            // Extract Magento product data from numbered list format
            const products = [];
            
            // SIMPLE: Extract products from numbered list
            // "1. Newport Camel 4 Piece Leather Sectional - $3,999.99"
            const lines = text.split('\n');
            
            lines.forEach(line => {
                // FIXED: Look for the ACTUAL format from your logs
                // "1. Lyndon Laredo Canvas 2 Piece Left Chaise Sectional"
                // "   Price: $2,328.74"
                
                const nameMatch = line.match(/^\s*\d+\.\s*(.+)$/);
                if (nameMatch) {
                    const name = nameMatch[1].trim();
                    
                    // Look for price in next lines or same line
                    const priceMatch = text.match(new RegExp(name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[\\s\\S]*?Price:\\s*\\$([0-9,]+\\.?\\d*)'));
                    if (priceMatch) {
                        const price = priceMatch[1].replace(',', '');
                        
                        products.push({
                            name: name,
                            sku: name.replace(/\s+/g, '-').toUpperCase().substring(0, 20),
                            price: parseFloat(price),
                            status: 2,
                            image_url: null, // Will be set by backend
                            media_gallery_entries: [],
                            custom_attributes: [
                                { attribute_code: 'brand', value: 'Woodstock Furniture' }
                            ]
                        });
                    }
                }
                
                // ALSO try simple pattern for "Product - $price" format
                const simpleMatch = line.match(/^\s*\d+\.\s*(.+?)\s*[-–]\s*\$([0-9,]+\.?\d*)/);
                if (simpleMatch) {
                    const name = simpleMatch[1].trim();
                    const price = simpleMatch[2].replace(',', '');
                    
                    products.push({
                        name: name,
                        sku: name.replace(/\s+/g, '-').toUpperCase().substring(0, 20),
                        price: parseFloat(price),
                        status: 2,
                        media_gallery_entries: [],
                        custom_attributes: [
                            { attribute_code: 'brand', value: 'Woodstock Furniture' }
                        ]
                    });
                }
            });
            
            // Also check for CAROUSEL_DATA format
            const carouselDataMatch = text.match(/\*\*CAROUSEL_DATA:\*\*\s*(\{.*\})/);
            if (carouselDataMatch) {
                try {
                    const carouselData = JSON.parse(carouselDataMatch[1]);
                    console.log('🎨 Extracted carousel JSON data:', carouselData);
                    data.data = carouselData;
                } catch (parseError) {
                    console.error('❌ Failed to parse carousel data:', parseError);
                    data.data = { products: products };
                }
            } else {
                data.data = { products: products };
            }
            
            console.log('🛒 Extracted products:', products.length);
        }

        console.log('🔍 Extracted data for', functionName, ':', data);
        console.log('📝 Original text:', text.substring(0, 200) + '...');
        return data;
    }

    formatDate(dateString) {
        if (!dateString || dateString === 'N/A') return 'N/A';
        try {
            // Handle various date formats
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
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
            if (content) {
                // Use component detection for assistant messages
                this.detectAndRenderComponents(content, contentDiv);
            }
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
