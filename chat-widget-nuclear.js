(() => {
  if (window.__aiPrlAssistLoaded) return;
  window.__aiPrlAssistLoaded = true;

  // Global namespace - preserve existing config
  const existingConfig = window.ChatWidget || {};
  window.ChatWidget = window.ChatWidget || {};

  // Setup function - called by client
  window.ChatWidget.setup = async (config) => {
    const {
      siteId,
      analytics = true,
      apiBase = null
    } = config;

    if (!siteId) {
      console.error('[AI PRL Assist] Missing required parameter: siteId');
      return;
    }

    // Load configuration from database
    let finalConfig = null;
    try {
      const baseUrl = apiBase || window.location.origin;
      const response = await fetch(`${baseUrl}/api/load-config?siteId=${siteId}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.config) {
          finalConfig = data.config;
          if (analytics) {
            console.log(`[AI PRL Assist] Loaded config from database for siteId: ${siteId}`, {
              clientName: data.clientName,
              source: 'database',
              updatedAt: data.updatedAt
            });
          }
        }
      }
    } catch (error) {
      if (analytics) console.error(`[AI PRL Assist] Error loading config for siteId: ${siteId}`, error);
    }

    if (!finalConfig) {
      console.error('[AI PRL Assist] No configuration found for siteId:', siteId);
      return;
    }

    // Enable console logging if global analytics is enabled
    if (analytics && window.ChatWidget.analytics && window.ChatWidget.analytics.console) {
      finalConfig.analytics = finalConfig.analytics || {};
      finalConfig.analytics.console = true;
    }

    // Build chat URL with UTM passthrough
    const buildChatUrl = () => {
      const baseUrl = finalConfig.chatUrl;
      const url = new URL(baseUrl);
      
      // Add current page context
      url.searchParams.set('embed', '1');
      url.searchParams.set('host', location.hostname);
      url.searchParams.set('page', location.href);
      if (document.referrer) url.searchParams.set('ref', document.referrer);
      
      // Capture and pass UTM parameters
      if (finalConfig.rules.appendUTM) {
        const currentParams = new URLSearchParams(location.search);
        ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(param => {
          const value = currentParams.get(param);
          if (value) url.searchParams.set(param, value);
        });
      }
      
      return url.toString();
    };

    // Webhook system
    const sendWebhook = (eventType, data = {}) => {
      if (!finalConfig.webhookUrl || !finalConfig.webhookEvents.includes(eventType)) return;
      
      const payload = {
        event: eventType,
        timestamp: new Date().toISOString(),
        siteId: siteId,
        page: location.href,
        host: location.hostname,
        userAgent: navigator.userAgent,
        ...data
      };

      fetch(finalConfig.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).catch(error => {
        if (finalConfig.analytics.console) {
          console.warn('[AI PRL Assist] Webhook failed:', error);
        }
      });
    };

    // Generate dynamic CSS from config
    const generateCSS = () => {
      const bubble = finalConfig.bubble;
      const teaser = finalConfig.teaser;
      const overlay = finalConfig.overlay;
      const onlineIndicator = finalConfig.onlineIndicator || {};
      const customStyles = finalConfig.customStyles || {};

      return `
        <style>
          .ai-prl-chat-bubble {
            position: fixed;
            ${bubble.position === 'bl' ? 'left: 20px' : 'right: 20px'};
            bottom: 20px;
            width: ${bubble.size}px;
            height: ${bubble.size}px;
            background: ${bubble.bg};
            ${bubble.outline ? `outline: ${bubble.outlineWidth || '2px'} solid ${bubble.outline};` : ''}
            ${bubble.outlineOffset ? `outline-offset: ${bubble.outlineOffset};` : ''}
            border-radius: 50%;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: ${bubble.zIndex || 2147483647};
            transition: transform 0.2s ease;
            ${bubble.pulse ? 'animation: ai-prl-pulse 1.2s infinite;' : ''}
          }
          
          .ai-prl-chat-bubble:hover {
            transform: scale(1.1);
          }
          
          .ai-prl-chat-bubble img {
            width: ${customStyles.bubbleImageWidth || '70%'};
            height: ${customStyles.bubbleImageHeight || '70%'};
            object-fit: ${customStyles.bubbleImageFit || 'contain'};
            ${customStyles.bubbleImageTransform ? `transform: ${customStyles.bubbleImageTransform};` : ''}
            ${customStyles.bubbleImageBorderRadius ? `border-radius: ${customStyles.bubbleImageBorderRadius};` : ''}
          }
          
          .ai-prl-chat-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: ${overlay.bg};
            z-index: ${(bubble.zIndex || 2147483647) - 1};
            display: none !important; /* 🔑 keep hidden until ChatWidget.open() */
          }
          
          .ai-prl-chat-iframe {
            width: 100%;
            height: 100%;
            border: none;
          }
          
          .ai-prl-chat-close {
            position: fixed;
            ${bubble.position === 'bl' ? 'left: 20px' : 'right: 20px'};
            bottom: ${parseInt(overlay.windowHeight) + 40}px;
            background: #fff;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 8px 12px;
            font: 700 12px/1 system-ui, -apple-system, Segoe UI, Roboto;
            cursor: pointer;
            z-index: ${bubble.zIndex || 2147483647};
            display: none !important; /* 🔑 keep hidden until ChatWidget.open() */
          }
          
          ${teaser.enabled ? `
          .ai-prl-teaser {
            position: fixed;
            ${bubble.position === 'bl' ? 'left: 20px' : 'right: 20px'};
            bottom: ${bubble.size + 30}px;
            background: ${teaser.bg || '#ffffff'};
            color: ${teaser.color || '#1c1c1e'};
            ${teaser.border ? `border: ${teaser.border};` : 'border: 1px solid #e9ecef;'}
            border-radius: ${teaser.borderRadius || '12px'};
            padding: ${teaser.padding || '12px 16px'};
            ${teaser.boxShadow ? `box-shadow: ${teaser.boxShadow};` : 'box-shadow: 0 4px 20px rgba(0,0,0,0.15);'}
            z-index: ${bubble.zIndex || 2147483647};
            ${teaser.minWidth ? `min-width: ${teaser.minWidth};` : ''}
            ${teaser.maxWidth ? `max-width: ${teaser.maxWidth};` : 'max-width: 280px;'}
            animation: ai-prl-bounce 0.5s ease-out;
            display: none;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            cursor: pointer;
            font-family: ${teaser.fontFamily || 'system-ui, -apple-system, Segoe UI, Roboto'};
            font-weight: ${teaser.fontWeight || '600'};
            font-size: ${teaser.fontSize || '14px'};
          }
          
          .ai-prl-teaser-text {
            flex-grow: 1;
          }
          
          .ai-prl-teaser-close {
            background: none;
            border: none;
            font-size: 20px;
            color: #8e8e93;
            cursor: pointer;
            padding: 0;
            line-height: 1;
          }
          ` : ''}
          
          ${onlineIndicator.enabled ? `
          .ai-prl-online-indicator {
            position: fixed;
            width: ${onlineIndicator.size || 18}px;
            height: ${onlineIndicator.size || 18}px;
            border-radius: 50%;
            background-color: ${onlineIndicator.color || '#12a712'};
            z-index: ${(bubble.zIndex || 2147483647) + 1};
            ${onlineIndicator.border ? `border: ${onlineIndicator.border};` : ''}
            ${bubble.position === 'bl' ? `left: ${onlineIndicator.offsetX || '12px'};` : `right: ${onlineIndicator.offsetX || '12px'};`}
            bottom: ${onlineIndicator.offsetY || '58px'};
            ${onlineIndicator.boxShadow ? `box-shadow: ${onlineIndicator.boxShadow};` : ''}
            ${onlineIndicator.pulse ? 'animation: ai-prl-online-pulse 1.2s infinite;' : ''}
          }
          ` : ''}
          
          @keyframes ai-prl-pulse {
            0% { box-shadow: 0 0 0 0 ${bubble.bg}66; }
            70% { box-shadow: 0 0 0 10px ${bubble.bg}00; }
            100% { box-shadow: 0 0 0 0 ${bubble.bg}00; }
          }
          
          @keyframes ai-prl-bounce {
            0% { opacity: 0; transform: translateY(20px) scale(0.8); }
            50% { opacity: 1; transform: translateY(-5px) scale(1.05); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
          }
          
          /* Open Modal Styles */
          .ai-prl-open-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: ${(bubble.zIndex || 2147483647) + 10};
            display: flex;
            align-items: center;
            justify-content: center;
          }
          
          .ai-prl-modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            cursor: pointer;
          }
          
          .ai-prl-modal-content {
            position: relative;
            background: white;
            border-radius: 16px;
            padding: 24px;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: ai-prl-modal-appear 0.3s ease-out;
          }
          
          .ai-prl-modal-content h3 {
            margin: 0 0 20px 0;
            font-size: 18px;
            font-weight: 600;
            color: #1c1c1e;
            text-align: center;
            font-family: system-ui, -apple-system, Segoe UI, Roboto;
          }
          
          .ai-prl-modal-options {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 20px;
          }
          
          .ai-prl-modal-btn {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            background: white;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: system-ui, -apple-system, Segoe UI, Roboto;
            text-align: left;
          }
          
          .ai-prl-modal-btn:hover {
            border-color: #007AFF;
            background: #f8f9ff;
            transform: translateY(-1px);
          }
          
          .ai-prl-modal-btn-overlay:hover {
            border-color: #FF9500;
            background: #fff8f0;
          }
          
          .ai-prl-modal-icon {
            font-size: 24px;
            flex-shrink: 0;
          }
          
          .ai-prl-modal-text {
            font-weight: 600;
            font-size: 16px;
            color: #1c1c1e;
            flex-grow: 1;
          }
          
          .ai-prl-modal-subtext {
            font-size: 12px;
            color: #8e8e93;
            font-weight: 400;
          }
          
          .ai-prl-modal-close {
            position: absolute;
            top: 12px;
            right: 12px;
            background: none;
            border: none;
            font-size: 20px;
            color: #8e8e93;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: background 0.2s ease;
          }
          
          .ai-prl-modal-close:hover {
            background: #f2f2f7;
          }
          
          @keyframes ai-prl-modal-appear {
            0% { opacity: 0; transform: scale(0.9) translateY(20px); }
            100% { opacity: 1; transform: scale(1) translateY(0); }
          }
          
          ${onlineIndicator.enabled && onlineIndicator.pulse ? `
          @keyframes ai-prl-online-pulse {
            0% { box-shadow: 0 0 0 0 ${onlineIndicator.color}70; }
            70% { box-shadow: 0 0 0 8px ${onlineIndicator.color}00; }
            100% { box-shadow: 0 0 0 0 ${onlineIndicator.color}00; }
          }
          ` : ''}
          
          @media (min-width: 768px) {
            .ai-prl-chat-overlay {
              display: none !important; /* ensure hidden until JS explicitly opens it */
              align-items: ${overlay.windowMode ? 'flex-end' : 'center'};
              justify-content: ${bubble.position === 'bl' ? 'flex-start' : 'flex-end'};
              padding: 20px;
            }
            .ai-prl-chat-iframe {
              width: ${overlay.windowMode ? overlay.windowWidth : '100%'};
              height: ${overlay.windowMode ? overlay.windowHeight : '100%'};
              border-radius: ${overlay.windowMode ? '12px' : '0'};
              box-shadow: ${overlay.windowMode ? '0 20px 60px rgba(0,0,0,0.3)' : 'none'};
              margin-bottom: ${overlay.windowMode ? '80px' : '0'};
            }
            .ai-prl-chat-close {
              display: none !important; /* only JS can reveal this */
            }
          }
        </style>
      `;
    };

    // Create widget HTML
    const createWidget = () => {
      const bubble = finalConfig.bubble;
      const teaser = finalConfig.teaser;
      const onlineIndicator = finalConfig.onlineIndicator || {};

      const widget = document.createElement('div');
      widget.innerHTML = `
        ${generateCSS()}
        
        <div class="ai-prl-chat-bubble" title="${bubble.label}">
          <img src="${bubble.iconUrl}" alt="Chat" />
        </div>
        
        ${teaser.enabled ? `
        <div class="ai-prl-teaser" onclick="window.ChatWidget.open()">
          <span class="ai-prl-teaser-text">${teaser.text}</span>
          <button class="ai-prl-teaser-close" onclick="event.stopPropagation(); window.ChatWidget.closeTeaser()">&times;</button>
        </div>
        ` : ''}
        
        ${onlineIndicator.enabled ? `
        <div class="ai-prl-online-indicator"></div>
        ` : ''}
        
        <!-- Open Modal -->
        <div class="ai-prl-open-modal" style="display: none;">
          <div class="ai-prl-modal-backdrop" onclick="window.ChatWidget.hideOpenModal()"></div>
          <div class="ai-prl-modal-content">
            <h3>How would you like to open the chat?</h3>
            <div class="ai-prl-modal-options">
              <button class="ai-prl-modal-btn ai-prl-modal-btn-overlay" onclick="window.ChatWidget.openInOverlay()">
                <span class="ai-prl-modal-icon">💬</span>
                <span class="ai-prl-modal-text">Open Here</span>
                <span class="ai-prl-modal-subtext">(Development stage only)</span>
              </button>
              <button class="ai-prl-modal-btn ai-prl-modal-btn-newtab" onclick="window.ChatWidget.openInNewTab()">
                <span class="ai-prl-modal-icon">🔗</span>
                <span class="ai-prl-modal-text">Open in New Tab</span>
                <span class="ai-prl-modal-subtext">(Recommended)</span>
              </button>
            </div>
            <button class="ai-prl-modal-close" onclick="window.ChatWidget.hideOpenModal()">✕</button>
          </div>
        </div>
        
        ${!finalConfig.noOverlay ? `
        <div class="ai-prl-chat-overlay" onclick="window.ChatWidget.close()">
          <iframe class="ai-prl-chat-iframe" src="about:blank"></iframe>
        </div>
        
        <button class="ai-prl-chat-close" onclick="window.ChatWidget.close()">✕ Close</button>
        ` : `
        <div class="ai-prl-chat-overlay" style="display: none;" onclick="window.ChatWidget.close()">
          <iframe class="ai-prl-chat-iframe" src="about:blank"></iframe>
        </div>
        
        <button class="ai-prl-chat-close" style="display: none;" onclick="window.ChatWidget.close()">✕ Close</button>
        `}
      `;
      
      document.body.appendChild(widget);
      return widget;
    };

    // Initialize
    const init = () => {
      const widget = createWidget();
      const overlay = widget.querySelector('.ai-prl-chat-overlay');
      const iframe = widget.querySelector('.ai-prl-chat-iframe');
      const closeBtn = widget.querySelector('.ai-prl-chat-close');
      const bubble = widget.querySelector('.ai-prl-chat-bubble');
      const teaser = widget.querySelector('.ai-prl-teaser');

      // Ensure overlay and close button are hidden on init
      if (overlay) overlay.style.display = 'none';
      if (closeBtn) closeBtn.style.display = 'none';
      if (iframe) iframe.src = 'about:blank';
      
      // Ensure modal is hidden on init
      const modal = widget.querySelector('.ai-prl-open-modal');
      if (modal) modal.style.display = 'none';

      // Add proper event binding for bubble click
      if (bubble) {
        bubble.addEventListener('click', () => {
          window.ChatWidget.showOpenModal();
        });
      }

      let chatOpened = false;

      // Public API
      window.ChatWidget.open = () => {
        const chatUrl = buildChatUrl();
        
        if (finalConfig.noOverlay) {
          // NO OVERLAY - open in new window/tab
          window.open(chatUrl, '_blank', 'width=420,height=650,scrollbars=yes,resizable=yes');
        } else {
          // Normal overlay behavior
          iframe.src = chatUrl;
          overlay.style.display = window.innerWidth >= 768 ? 'flex' : 'block';
          if (closeBtn) closeBtn.style.display = window.innerWidth >= 768 ? 'block' : 'none';
        }
        
        chatOpened = true;
        sendWebhook('chat_opened', { chatUrl });
        
        if (finalConfig.analytics.console) {
          console.log('[AI PRL Assist] Chat opened with URL:', chatUrl, finalConfig.noOverlay ? '(new window)' : '(overlay)');
        }
      };

      window.ChatWidget.close = () => {
        if (overlay) {
          overlay.style.display = 'none';
          if (closeBtn) closeBtn.style.display = 'none';
          if (iframe) iframe.src = 'about:blank';
        }
        chatOpened = false;
        
        sendWebhook('chat_closed');
        
        if (finalConfig.analytics.console) {
          console.log('[AI PRL Assist] Chat closed');
        }
      };

      window.ChatWidget.closeTeaser = () => {
        if (teaser) teaser.style.display = 'none';
      };

      window.ChatWidget.showTeaser = () => {
        if (teaser) teaser.style.display = 'flex';
      };

      // Modal functions
      window.ChatWidget.showOpenModal = () => {
        const modal = widget.querySelector('.ai-prl-open-modal');
        if (modal) modal.style.display = 'flex';
      };

      window.ChatWidget.hideOpenModal = () => {
        const modal = widget.querySelector('.ai-prl-open-modal');
        if (modal) modal.style.display = 'none';
      };

      window.ChatWidget.openInOverlay = () => {
        window.ChatWidget.hideOpenModal();
        window.ChatWidget.open();
      };

      window.ChatWidget.openInNewTab = () => {
        const chatUrl = buildChatUrl();
        window.open(chatUrl, '_blank', 'width=420,height=650,scrollbars=yes,resizable=yes');
        window.ChatWidget.hideOpenModal();
        sendWebhook('chat_opened', { chatUrl, method: 'new_tab' });
        
        if (finalConfig.analytics.console) {
          console.log('[AI PRL Assist] Chat opened in new tab with URL:', chatUrl);
        }
      };

      // Event handlers
      if (overlay) {
        overlay.addEventListener('click', (e) => {
          if (e.target === overlay && !finalConfig.noOverlay) {
            // Only close on overlay click if there IS a dark overlay
            window.ChatWidget.close();
          }
        });
      }
      
      if (closeBtn) {
        closeBtn.addEventListener('click', window.ChatWidget.close);
      }

      // ESC key to close
      if (finalConfig.overlay.closeOnEsc) {
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape') {
            // Close modal if open, otherwise close chat
            const modal = widget.querySelector('.ai-prl-open-modal');
            if (modal && modal.style.display === 'flex') {
              window.ChatWidget.hideOpenModal();
            } else {
              window.ChatWidget.close();
            }
          }
        });
      }

      // Show bubble after delay
      setTimeout(() => {
        bubble.style.display = 'flex';
        if (finalConfig.analytics.console) {
          console.log('[AI PRL Assist] Bubble shown');
        }
      }, finalConfig.triggers.showBubbleAfterMs);

      // Show teaser after delay
      if (finalConfig.teaser.enabled) {
        setTimeout(() => {
          window.ChatWidget.showTeaser();
          sendWebhook('teaser_shown');
          if (finalConfig.analytics.console) {
            console.log('[AI PRL Assist] Teaser shown');
          }
        }, finalConfig.teaser.delayMs);

        // Auto-close teaser
        if (finalConfig.teaser.autocloseMs > 0) {
          setTimeout(() => {
            window.ChatWidget.closeTeaser();
            sendWebhook('teaser_autoclosed');
          }, finalConfig.teaser.delayMs + finalConfig.teaser.autocloseMs);
        }
      }

      // Auto-open after delay
      if (finalConfig.triggers.openAfterMs > 0) {
        setTimeout(() => {
          window.ChatWidget.open();
        }, finalConfig.triggers.openAfterMs);
      }

      // Exit intent trigger
      if (finalConfig.triggers.triggerOnExitIntent) {
        document.addEventListener('mouseleave', (e) => {
          if (e.clientY < 0) {
            window.ChatWidget.open();
          }
        });
      }

      // Scroll trigger
      if (finalConfig.triggers.triggerOnScrollPercent > 0) {
        let triggered = false;
        window.addEventListener('scroll', () => {
          if (triggered) return;
          const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
          if (scrollPercent >= finalConfig.triggers.triggerOnScrollPercent) {
            window.ChatWidget.open();
            triggered = true;
          }
        });
      }

      if (finalConfig.analytics.console) {
        console.log('[AI PRL Assist] Widget ready with config:', {
          siteId: siteId,
          chatUrl: finalConfig.chatUrl,
          triggers: finalConfig.triggers,
          customizations: Object.keys(finalConfig).length
        });
      }
    };

    // Wait for DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  };
  // Auto-initialize like OneSignal pattern
  const autoInit = () => {
    // Check if existingConfig has siteId (like your Webflow code)
    if (existingConfig && existingConfig.siteId) {
      window.ChatWidget.setup({ siteId: existingConfig.siteId });
      return;
    }
    
    // Fallback: Check URL params
    const urlParams = new URLSearchParams(window.location.search);
    const siteId = urlParams.get('siteId');
    if (siteId) {
      window.ChatWidget.setup({ siteId });
    }
  };
  
  // Try auto-init immediately and on DOM ready
  autoInit();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  }

})();
