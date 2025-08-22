// Woodstock Outlet Chat - Professional Implementation
class WoodstockChat {
    constructor() {
        this.apiBase = window.location.origin;
        this.isConnected = false;
        this.isThinking = false;
        
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

    generateSessionId() {
        const id = 'woodstock_' + Math.random().toString(36).substr(2, 16);
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

    init() {
        console.log('🚀 Initializing Woodstock Chat...');
        console.log('🆔 Session ID:', this.sessionId);
        console.log('👤 User Identifier:', this.userIdentifier);
        
        // Event Listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResize());
        
        // Test connection
        this.testConnection();
        
        // Focus input
        setTimeout(() => this.messageInput.focus(), 500);
        
        console.log('✅ Woodstock Chat initialized!');
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
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
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
            user_identifier: this.userIdentifier
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
                                contentDiv.textContent = fullResponse;
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

    formatAsHTML(text) {
        // DETECT JSON FUNCTION RESULTS (like original system)
        try {
            // Check if text contains JSON function result
            const jsonMatch = text.match(/\{[^{}]*"function"[^{}]*"status"[^}]*\}/);
            if (jsonMatch) {
                const functionResult = JSON.parse(jsonMatch[0]);
                console.log('🔧 Function result detected:', functionResult);
                
                // Render HTML component based on function type
                return this.renderFunctionComponent(functionResult);
            }
        } catch (e) {
            console.log('📝 No JSON detected, using markdown formatting');
        }
        
        // Fallback: Convert markdown-style formatting to HTML
        let html = text;
        html = html
            .replace(/\*\*\*(.+?)\*\*\*/g, '<strong style="color: var(--woodstock-red);">$1</strong>')
            .replace(/\*\*(.+?)\*\*/g, '<strong style="color: var(--woodstock-navy);">$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/`(.+?)`/g, '<code style="background: rgba(0,33,71,0.1); padding: 2px 4px; border-radius: 3px;">$1</code>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
        
        if (!html.includes('<')) {
            html = `<p>${html}</p>`;
        }
        
        return html;
    }

    renderFunctionComponent(functionResult) {
        const { function: funcName, status, data, message } = functionResult;
        
        if (status !== 'success') {
            return `<div class="error-message">❌ ${message || 'Function failed'}</div>`;
        }
        
        // Render based on function type
        switch (funcName) {
            case 'getCustomerByPhone':
            case 'getCustomerByEmail':
                return `
                    <div class="customer-card">
                        <h4>✅ Customer Found</h4>
                        <div><strong>📱 Phone:</strong> ${data.phone}</div>
                        <div><strong>🆔 Customer ID:</strong> ${data.customerid}</div>
                        <div><strong>👤 Name:</strong> ${data.firstname} ${data.lastname}</div>
                        <div><strong>📧 Email:</strong> ${data.email}</div>
                        <div><strong>🏠 Address:</strong> ${data.address}</div>
                        <div><strong>📮 ZIP:</strong> ${data.zipcode}</div>
                    </div>
                `;
            
            case 'getOrdersByCustomer':
                let orderHtml = '<div class="order-summary"><h4>📦 Customer Orders</h4>';
                data.orders.forEach((order, i) => {
                    orderHtml += `
                        <div class="order-item">
                            <div>
                                <strong>Order #${i+1}:</strong> ${order.orderid}<br>
                                <strong>Status:</strong> ${order.status}<br>
                                <strong>Date:</strong> ${order.orderdate}
                            </div>
                            <div class="price-tag">$${order.sum}</div>
                        </div>
                    `;
                });
                orderHtml += '</div>';
                return orderHtml;
            
            default:
                return `<div class="success-message">✅ ${message}</div>`;
        }
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
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
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
