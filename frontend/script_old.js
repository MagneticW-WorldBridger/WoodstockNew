// LOFT Chat Frontend - JavaScript Logic
class LoftChat {
    constructor() {
        // 🔥 BUG-007 FIX: Use environment-based URL configuration
        this.apiBase = (typeof window !== 'undefined' && window.BACKEND_URL) ? window.BACKEND_URL : 'http://localhost:8001';
        this.isConnected = false;
        this.isThinking = false;
        
        // Session management for memory
        this.sessionId = localStorage.getItem('loft-chat-session') || this.generateSessionId();
        this.userIdentifier = localStorage.getItem('loft-chat-user') || null;
        this.messageHistory = [];
        
        // DOM Elements
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.charCount = document.getElementById('charCount');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        this.init();
    }

    generateSessionId() {
        const id = 'session_' + Math.random().toString(36).substr(2, 16);
        localStorage.setItem('loft-chat-session', id);
        console.log('🆔 Generated session ID:', id);
        return id;
    }

    detectUserIdentifier(message) {
        // Phone number pattern
        const phoneMatch = message.match(/\b\d{3}-\d{3}-\d{4}\b/);
        if (phoneMatch && phoneMatch[0]) {
            this.userIdentifier = phoneMatch[0];
            localStorage.setItem('loft-chat-user', this.userIdentifier);
            console.log('🔍 Auto-detected user identifier:', this.userIdentifier);
            return this.userIdentifier;
        }
        
        // Email pattern  
        const emailMatch = message.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
        if (emailMatch && emailMatch[0]) {
            this.userIdentifier = emailMatch[0];
            localStorage.setItem('loft-chat-user', this.userIdentifier);
            console.log('🔍 Auto-detected user identifier:', this.userIdentifier);
            return this.userIdentifier;
        }
        
        return null;
    }

    init() {
        console.log('🚀 Initializing LOFT Chat...');
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
        
        console.log('✅ LOFT Chat initialized!');
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
            this.showError('Cannot connect to LOFT backend. Please check if server is running on port 8001.');
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
            this.statusDot.classList.add('thinking');
            this.statusText.textContent = 'AI is thinking...';
            this.sendButton.disabled = true;
        } else {
            this.statusDot.classList.remove('thinking');
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
        
        // Color coding for character count
        if (length > 900) {
            this.charCount.style.color = '#FCA5A5'; // Red
        } else if (length > 700) {
            this.charCount.style.color = '#FDE68A'; // Yellow
        } else {
            this.charCount.style.color = 'rgba(255, 255, 255, 0.5)'; // Default
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
            max_tokens: 1000,
            temperature: 0.7,
            session_id: this.sessionId,
            user_identifier: this.userIdentifier
        };
        
        console.log('📋 Request data:', {
            sessionId: this.sessionId,
            userIdentifier: this.userIdentifier,
            historyLength: this.messageHistory.length
        });

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
        const contentDiv = messageDiv.querySelector('.message-text');
        
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
                            // Format the final response with markdown
                            if (fullResponse.trim()) {
                                contentDiv.innerHTML = this.formatMessage(fullResponse);
                                this.messageHistory.push({ role: 'assistant', content: fullResponse });
                                console.log('💾 Added assistant response to history');
                            }
                            return;
                        }

                        try {
                            const parsed = JSON.parse(data);
                            const delta = parsed.choices?.[0]?.delta;
                            
                            if (delta?.content) {
                                // Acumular deltas incrementales (backend usa delta=True)
                                fullResponse += delta.content;
                                contentDiv.textContent = fullResponse;
                                this.scrollToBottom();
                            }
                            
                            // Check for function calls
                            if (delta?.tool_calls) {
                                console.log('🔧 Function call detected');
                                this.showFunctionCall(delta.tool_calls[0]);
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

    addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message-bubble ${role}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (role === 'assistant') {
            contentDiv.innerHTML = `
                <i class="fas fa-robot text-purple-400 mr-2"></i>
                <span class="message-text">${this.formatMessage(content)}</span>
            `;
        } else {
            contentDiv.innerHTML = `
                <span class="message-text">${this.formatMessage(content)}</span>
                <i class="fas fa-user text-blue-300 ml-2"></i>
            `;
        }
        
        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);
        
        this.scrollToBottom();
        return messageDiv;
    }

    formatMessage(text) {
        // Basic markdown-like formatting
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code class="bg-white/20 px-1 rounded">$1</code>')
            .replace(/\n/g, '<br>');
        
        // Format phone numbers
        formatted = formatted.replace(/(\d{3}-\d{3}-\d{4})/g, '<span class="font-mono text-blue-300">$1</span>');
        
        // Format email addresses
        formatted = formatted.replace(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g, '<span class="font-mono text-green-300">$1</span>');
        
        return formatted;
    }

    showTypingIndicator() {
        const existingIndicator = document.querySelector('.typing-indicator');
        if (existingIndicator) return;
        
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <i class="fas fa-robot text-purple-400 mr-2"></i>
            <span class="text-white/70 mr-3">AI is thinking</span>
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
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    showFunctionCall(toolCall) {
        const functionDiv = document.createElement('div');
        functionDiv.className = 'function-call';
        functionDiv.innerHTML = `
            <i class="fas fa-cogs mr-2"></i>
            <span>Calling: ${toolCall.function?.name || 'function'}</span>
        `;
        
        // Add to last assistant message
        const lastMessage = this.messagesContainer.querySelector('.assistant-message:last-child .message-content');
        if (lastMessage) {
            lastMessage.appendChild(functionDiv);
        }
        
        this.scrollToBottom();
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message-bubble assistant-message';
        errorDiv.innerHTML = `
            <div class="message-content">
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    ${message}
                </div>
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

    // Mobile optimizations
    handleMobileOptimizations() {
        // Prevent zoom on input focus (iOS)
        if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
            this.messageInput.addEventListener('focus', () => {
                document.querySelector('meta[name=viewport]').setAttribute(
                    'content', 
                    'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
                );
            });
            
            this.messageInput.addEventListener('blur', () => {
                document.querySelector('meta[name=viewport]').setAttribute(
                    'content', 
                    'width=device-width, initial-scale=1.0'
                );
            });
        }
        
        // Handle mobile keyboard
        window.addEventListener('resize', () => {
            this.scrollToBottom();
        });
    }

    // Utility methods
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    // Initialize mobile optimizations
    initMobile() {
        this.handleMobileOptimizations();
        
        // Touch feedback
        document.addEventListener('touchstart', () => {}, { passive: true });
        
        // Prevent double-tap zoom
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOM loaded, initializing LOFT Chat...');
    
    const chat = new LoftChat();
    
    // Initialize mobile optimizations
    chat.initMobile();
    
    // Debug info
    console.log('🔧 LOFT Chat ready!');
    console.log('📱 Backend API:', chat.apiBase);
    console.log('🌐 Frontend URL:', window.location.href);
    
    // Global access for debugging
    window.loftChat = chat;
});

// Service Worker Registration (for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('✅ SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('❌ SW registration failed: ', registrationError);
            });
    });
}

// Utility Functions
function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit'
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle visibility changes (for performance)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('🔇 App hidden, reducing activity...');
    } else {
        console.log('👁️ App visible, resuming normal activity...');
        if (window.loftChat && !window.loftChat.isConnected) {
            window.loftChat.testConnection();
        }
    }
});

// Global error handler
window.addEventListener('error', (e) => {
    console.error('🚨 Global error:', e.error);
    if (window.loftChat) {
        window.loftChat.showError('An unexpected error occurred. Please refresh the page.');
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('🌐 Back online');
    if (window.loftChat) {
        window.loftChat.testConnection();
    }
});

window.addEventListener('offline', () => {
    console.log('📴 Gone offline');
    if (window.loftChat) {
        window.loftChat.setConnected(false);
    }
});

console.log('📁 LOFT Chat script loaded successfully!');
