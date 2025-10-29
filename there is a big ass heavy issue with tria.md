there is a big ass heavy issue with triangulation here, 

this is the settings for my dynamic webchat: 
{
    "rules": {
        "maxWidth": 99999,
        "minWidth": 0,
        "appendUTM": true,
        "excludePaths": [
            "/admin/*",
            "/staff/*"
        ],
        "includePaths": [
            "*"
        ],
        "showOnMobile": true,
        "showOnDesktop": true,
        "frequencyCapHours": 24
    },
    "bubble": {
        "bg": "#1e40af",
        "size": 85,
        "color": "#ffffff",
        "label": "Woodstock AI",
        "pulse": true,
        "zIndex": 2147483647,
        "iconUrl": "https://storage.googleapis.com/msgsndr/ecow5j0SgdAz2vzC0C4Q/media/68d2ca791dbafc4004869120.png",
        "outline": "#3b82f6",
        "position": "br",
        "outlineWidth": "2px",
        "outlineOffset": "0px"
    },
    "teaser": {
        "bg": "#ffffff",
        "text": "Need furniture help? Chat with Woodstock AI!",
        "color": "#1e40af",
        "border": "2px solid #3b82f6",
        "delayMs": 3000,
        "enabled": true,
        "fontSize": "14px",
        "maxWidth": "350px",
        "minWidth": "250px",
        "boxShadow": "0 4px 12px rgba(30,64,175,0.2)",
        "fontFamily": "Arial, sans-serif",
        "fontWeight": "600",
        "autocloseMs": 15000,
        "borderRadius": "8px"
    },
    "apiBase": "https://dynamiccode-ochre.vercel.app",
    "chatUrl": "https://woodstock.demo.aiprlassist.com",
    "overlay": {
        "bg": "rgba(0,0,0,0.6)",
        "closeOnEsc": true,
        "windowMode": true,
        "windowWidth": "450px",
        "windowHeight": "700px"
    },
    "triggers": {
        "openAfterMs": 0,
        "showBubbleAfterMs": 2000,
        "triggerOnExitIntent": false,
        "triggerOnScrollPercent": 0
    },
    "analytics": {
        "console": true,
        "trackOpens": true
    },
    "noOverlay": false,
    "webhookUrl": "https://dynamiccode-ochre.vercel.app/api/internal-webhook",
    "fallbackUrl": "https://woodstock.demo.aiprlassist.com",
    "customStyles": {
        "bubbleImageFit": "cover",
        "bubbleImageWidth": "100%",
        "bubbleImageHeight": "100%",
        "bubbleImageTransform": "none",
        "bubbleImageBorderRadius": "50%"
    },
    "webhookEvents": [
        "page_view",
        "bubble_shown",
        "chat_opened",
        "teaser_shown",
        "teaser_message_received"
    ],
    "realTimeTeaser": {
        "apiKey": "woodstock_rt_key_2024",
        "enabled": true,
        "pollIntervalMs": 8000
    },
    "onlineIndicator": {
        "size": 16,
        "color": "#22c55e",
        "pulse": true,
        "border": "2px solid white",
        "enabled": true,
        "offsetX": "10px",
        "offsetY": "50px",
        "position": "bottom-right-offset",
        "boxShadow": "0 0 6px 1px rgba(34,197,94,0.4)"
    },
    "skipEmbedParams": true
}


and I have a script that is the one that I put on the website of my client which is: 

<script>
    window.ChatWidget = window.ChatWidget || {};
    window.ChatWidget.siteId = "woodstock_outlet";
    window.ChatWidget.apiBase = "https://dynamiccode-ochre.vercel.app";
    window.ChatWidget.analytics = { console: true };
  </script>

  <script
    async
    src="https://dynamiccode-ochre.vercel.app/chat-widget-nuclear.js"
  ></script>



Then the script that runs on my backend is pretty much this : 

(() => {
  if (window.__aiPrlAssistLoaded) return;
  window.__aiPrlAssistLoaded = true;

  // Global namespace - preserve existing config
  const existingConfig = window.ChatWidget || {};
  window.ChatWidget = window.ChatWidget || {};

  // Setup function - called by client
  window.ChatWidget.setup = async (config) => {
    // Generate session ID FIRST (only once)
    if (!window.ChatWidget._sessionId) {
      window.ChatWidget._sessionId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      window.ChatWidget._pageLoadTime = Date.now();
    }
    
    // Prevent double initialization
    if (window.ChatWidget._initialized || window.ChatWidget._initializing) {
      console.warn('[AI PRL Assist] ⚠️ Widget already initialized or initializing, skipping...');
      console.warn('[AI PRL Assist] Using existing session ID:', window.ChatWidget._sessionId);
      return;
    }
    
    // Mark as initializing to prevent race conditions
    window.ChatWidget._initializing = true;
    
    const {
      siteId,
      analytics = true,
      apiBase = null
    } = config;

    if (!siteId) {
      console.error('[AI PRL Assist] Missing required parameter: siteId');
      return;
    }

    // Load configuration - try embedded first, then database
    let finalConfig = null;
    
    // Check for embedded configuration first (no API call needed)
    if (window.ChatWidget.embeddedConfig) {
      finalConfig = window.ChatWidget.embeddedConfig;
      if (analytics) {
        console.log(`[AI PRL Assist] ✅ Using EMBEDDED config for siteId: ${siteId}`, {
          source: 'embedded',
          configSize: Object.keys(finalConfig).length
        });
      }
    } else {
      // Fallback to database fetch
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
        window.ChatWidget._initializing = false;
        return;
      }
    }

    if (!finalConfig) {
      console.error('[AI PRL Assist] No configuration found for siteId:', siteId);
      console.error('[AI PRL Assist] Tried: embedded config and database API');
      window.ChatWidget._initializing = false;
      return;
    }

    // Enable console logging if global analytics is enabled
    if (analytics && window.ChatWidget.analytics && window.ChatWidget.analytics.console) {
      finalConfig.analytics = finalConfig.analytics || {};
      finalConfig.analytics.console = true;
    }

    // Build chat URL with UTM passthrough
    const buildChatUrl = (useCleanUrl = false) => {
      const baseUrl = finalConfig.chatUrl;
      const url = new URL(baseUrl);
      
      // Check if we should skip embed parameters (for problematic chats)
      const skipEmbedParams = useCleanUrl || finalConfig.skipEmbedParams || false;
      
      if (!skipEmbedParams) {
        // Add current page context
        url.searchParams.set('embed', '1');
        url.searchParams.set('host', location.hostname);
        url.searchParams.set('page', location.href);
        if (document.referrer) url.searchParams.set('ref', document.referrer);
      }
      
      // Capture and pass UTM parameters
      if (finalConfig.rules.appendUTM) {
        const currentParams = new URLSearchParams(location.search);
        ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(param => {
          const value = currentParams.get(param);
          if (value) url.searchParams.set(param, value);
        });
      }
      
      if (finalConfig.analytics.console && skipEmbedParams) {
        console.log('[AI PRL Assist] 🧹 Using clean URL (no embed params)');
      }
      
      return url.toString();
    };

    // Smart triggering logic
    const calculateInteractionScore = () => {
      let score = 0;
      
      // High-value pages
      const highValuePages = ['/chairs', '/products', '/checkout', '/cart'];
      if (highValuePages.some(page => location.pathname.includes(page))) {
        score += 30;
      }
      
      // UTM campaigns
      const urlParams = new URLSearchParams(location.search);
      if (urlParams.get('utm_campaign')) score += 20;
      if (urlParams.get('utm_source') === 'facebook') score += 15;
      if (urlParams.get('utm_medium') === 'cpc') score += 10;
      
      // Custom parameters (customer identified)
      if (urlParams.get('customer_id')) score += 25;
      if (urlParams.get('customer_email')) score += 20;
      
      // Time on page (longer = more interested)
      const timeOnPage = Date.now() - (window.ChatWidget._pageLoadTime || Date.now());
      if (timeOnPage > 30000) score += 15; // 30+ seconds
      if (timeOnPage > 60000) score += 25; // 1+ minute
      
      return score;
    };

    const shouldTriggerAI = (sessionData) => {
      const now = Date.now();
      const timeSinceLastTeaser = now - sessionData.lastTeaserSent;
      const minInterval = 5 * 60 * 1000; // 5 minutes minimum between AI triggers
      
      // Don't trigger if too recent
      if (timeSinceLastTeaser < minInterval) {
        return false;
      }
      
      // Trigger conditions (OR logic - any one triggers)
      const conditions = [
        sessionData.interactionScore >= 50, // High interest score
        sessionData.pageViews >= 3, // Multiple page views
        location.pathname.includes('/checkout'), // Critical page
        location.pathname.includes('/cart'), // Shopping intent
        new URLSearchParams(location.search).get('customer_id') // Known customer
      ];
      
      return conditions.some(condition => condition);
    };

    // Extract UTM and custom parameters from URL
    const extractUrlData = () => {
      const urlParams = new URLSearchParams(location.search);
      const utmData = {};
      const customData = {};
      
      // Extract UTM parameters
      ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'].forEach(param => {
        const value = urlParams.get(param);
        if (value) utmData[param] = value;
      });
      
      // Extract custom parameters (customer_id, customer_email, etc.)
      urlParams.forEach((value, key) => {
        if (!key.startsWith('utm_') && key !== 'embed' && key !== 'host' && key !== 'page' && key !== 'ref') {
          customData[key] = value;
        }
      });
      
      return { utmData, customData };
    };

    // Webhook system with full data capture
    const sendWebhook = (eventType, data = {}) => {
      // Use internal webhook if no external webhook configured
      const webhookUrl = finalConfig.webhookUrl || `${finalConfig.apiBase || window.location.origin}/api/internal-webhook`;
      
      if (!finalConfig.webhookEvents.includes(eventType)) return;
      
      const { utmData, customData } = extractUrlData();
      
      const payload = {
        event: eventType,
        timestamp: new Date().toISOString(),
        siteId: siteId,
        sessionId: window.ChatWidget._sessionId, // Use the session ID generated at initialization
        
        // Page data
        page: {
          url: location.href,
          pathname: location.pathname,
          search: location.search,
          hash: location.hash,
          title: document.title,
          referrer: document.referrer
        },
        
        // UTM data
        utm: utmData,
        
        // Custom URL parameters (customer_id, customer_email, etc.)
        custom: customData,
        
        // Visitor data
        visitor: {
          userAgent: navigator.userAgent,
          language: navigator.language,
          platform: navigator.platform,
          screenWidth: screen.width,
          screenHeight: screen.height,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        },
        
        // Host data
        host: location.hostname,
        
        // Event-specific data
        ...data
      };

      if (finalConfig.analytics.console) {
        console.log('[AI PRL Assist] 📤 Sending webhook:', eventType, payload);
      }

      // Call custom webhook handler if provided
      if (window.ChatWidget.onWebhookSent) {
        try {
          window.ChatWidget.onWebhookSent(eventType, payload);
        } catch (e) {
          console.warn('[AI PRL Assist] Custom webhook handler failed:', e);
        }
      }

      // Always send webhook (internal or external)
      fetch(webhookUrl, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'X-Widget-Source': 'ai-prl-assist',
            'X-Site-ID': siteId,
            'X-Event-Type': eventType
          },
          body: JSON.stringify(payload)
        }).catch(error => {
          if (finalConfig.analytics.console) {
            console.error('[AI PRL Assist] Webhook failed:', error);
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
            align-items: center;
            justify-content: center;
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
        
        <!-- Open Modal - DISABLED: Direct bubble click now opens chat directly -->
        <!--
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
        -->
        
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
      if (overlay) overlay.style.setProperty('display', 'none', 'important');
      if (closeBtn) closeBtn.style.display = 'none';
      if (iframe) iframe.src = 'about:blank';
      
      // Modal functionality removed - direct bubble click now opens chat
      // const modal = widget.querySelector('.ai-prl-open-modal');
      // if (modal) modal.style.display = 'none';

      // Add proper event binding for bubble click - toggle open/close
      if (bubble) {
        bubble.addEventListener('click', () => {
          if (chatOpened) {
            window.ChatWidget.close();
          } else {
            window.ChatWidget.open();
          }
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
          if (finalConfig.analytics.console) {
            console.log('[AI PRL Assist] 🚀 OPENING OVERLAY - FULL DEBUG');
            console.log('[AI PRL Assist] Screen width:', window.innerWidth);
            console.log('[AI PRL Assist] Chat URL:', chatUrl);
            console.log('[AI PRL Assist] Overlay element:', overlay);
            console.log('[AI PRL Assist] Iframe element:', iframe);
            console.log('[AI PRL Assist] Parent domain:', window.location.hostname);
            console.log('[AI PRL Assist] Parent protocol:', window.location.protocol);
            console.log('[AI PRL Assist] Document referrer:', document.referrer);
          }
          
          // Add iframe event listeners for debugging
          iframe.addEventListener('load', () => {
            if (finalConfig.analytics.console) {
              console.log('[AI PRL Assist] ✅ IFRAME LOADED SUCCESSFULLY');
              console.log('[AI PRL Assist] Iframe src:', iframe.src);
              console.log('[AI PRL Assist] Iframe contentWindow:', iframe.contentWindow);
              
              // Try to check iframe content (may be blocked by CORS)
              try {
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (iframeDoc) {
                  console.log('[AI PRL Assist] Iframe document title:', iframeDoc.title);
                  console.log('[AI PRL Assist] Iframe document URL:', iframeDoc.URL);
                  
                  // Check for error messages in the iframe
                  const bodyText = iframeDoc.body ? iframeDoc.body.innerText : 'No body';
                  if (bodyText.toLowerCase().includes('error') || bodyText.toLowerCase().includes('permission')) {
                    console.error('[AI PRL Assist] 🚨 ERROR DETECTED IN IFRAME:', bodyText.substring(0, 200));
                  }
                } else {
                  console.log('[AI PRL Assist] Cannot access iframe document (CORS blocked)');
                }
              } catch (e) {
                console.log('[AI PRL Assist] Cannot access iframe content (CORS blocked):', e.message);
              }
            }
          });
          
          iframe.addEventListener('error', (e) => {
            if (finalConfig.analytics.console) {
              console.error('[AI PRL Assist] ❌ IFRAME ERROR:', e);
              console.error('[AI PRL Assist] Error details:', {
                type: e.type,
                target: e.target,
                message: e.message || 'No message'
              });
              console.log('[AI PRL Assist] Trying fallback URL...');
            }
            
            // Try fallback URL on error
            if (finalConfig.fallbackUrl && iframe.src !== finalConfig.fallbackUrl) {
              setTimeout(() => {
                iframe.src = finalConfig.fallbackUrl;
                if (finalConfig.analytics.console) {
                  console.log('[AI PRL Assist] 🔄 FALLBACK URL LOADED:', finalConfig.fallbackUrl);
                }
              }, 1000);
            }
          });
          
          iframe.src = chatUrl;
          overlay.style.setProperty('display', window.innerWidth >= 768 ? 'flex' : 'block', 'important');
          if (closeBtn) closeBtn.style.display = 'block'; // Always show close button
          
          if (finalConfig.analytics.console) {
            console.log('[AI PRL Assist] Overlay display set to:', overlay.style.display);
            console.log('[AI PRL Assist] 🔍 MONITORING IFRAME LOADING...');
            
            // Monitor iframe loading with timeout
            let loadingTimeout = setTimeout(() => {
              console.warn('[AI PRL Assist] ⏰ IFRAME TAKING TOO LONG TO LOAD (>10s)');
              console.log('[AI PRL Assist] Current iframe src:', iframe.src);
              console.log('[AI PRL Assist] Iframe readyState:', iframe.readyState);
              
              // Try fallback after timeout
              if (finalConfig.fallbackUrl && iframe.src !== finalConfig.fallbackUrl) {
                console.log('[AI PRL Assist] 🔄 SWITCHING TO FALLBACK DUE TO TIMEOUT');
                iframe.src = finalConfig.fallbackUrl;
              }
            }, 10000);
            
            // Clear timeout when iframe loads
            iframe.addEventListener('load', () => {
              clearTimeout(loadingTimeout);
            }, { once: true });
          }
        }
        
        chatOpened = true;
        
        // Close teaser when chat opens
        if (teaser) teaser.style.display = 'none';
        
        sendWebhook('chat_opened', { chatUrl });
        
        if (finalConfig.analytics.console) {
          console.log('[AI PRL Assist] Chat opened with URL:', chatUrl, finalConfig.noOverlay ? '(new window)' : '(overlay)');
        }
      };

      window.ChatWidget.close = () => {
        if (overlay) {
          overlay.style.setProperty('display', 'none', 'important');
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

      window.ChatWidget.showTeaser = (customMessage = null) => {
        if (teaser) {
          // If custom message provided, update teaser text
          if (customMessage) {
            const teaserTextElement = teaser.querySelector('.ai-prl-teaser-text');
            if (teaserTextElement) {
              teaserTextElement.textContent = customMessage;
              if (finalConfig.analytics.console) {
                console.log('[AI PRL Assist] 🎯 Custom teaser message:', customMessage);
              }
            }
          }
          // Make sure teaser is visible
          teaser.style.display = 'flex';
          teaser.style.opacity = '1';
          teaser.style.visibility = 'visible';
          
          // Add a subtle animation to draw attention
          teaser.style.transform = 'scale(1.05)';
          setTimeout(() => {
            teaser.style.transform = 'scale(1)';
          }, 200);
          
          if (finalConfig.analytics.console) {
            console.log('[AI PRL Assist] ✅ Teaser shown with message:', customMessage || 'default message');
          }
        } else if (finalConfig.analytics.console) {
          console.warn('[AI PRL Assist] ⚠️ Teaser element not found!');
        }
      };

      // Modal functions - DISABLED: Direct bubble click now opens chat directly
      /*
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
      */

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
            // Close chat directly (modal functionality removed)
            window.ChatWidget.close();
          }
        });
      }

      // DEBUG: Log iframe details for troubleshooting
      if (finalConfig.analytics.console) {
        console.log('[AI PRL Assist] 🔍 IFRAME DEBUG INFO:');
        console.log('[AI PRL Assist] Parent domain:', window.location.hostname);
        console.log('[AI PRL Assist] Parent URL:', window.location.href);
        console.log('[AI PRL Assist] Referrer:', document.referrer);
        console.log('[AI PRL Assist] User Agent:', navigator.userAgent);
      }

      // Smart triggering system
      const sessionData = {
        pageViews: 0,
        lastTeaserSent: 0,
        interactionScore: 0,
        startTime: Date.now()
      };

      // Increment page views and calculate interaction score
      sessionData.pageViews++;
      sessionData.interactionScore += calculateInteractionScore();

      // Send page_view webhook with smart triggering logic
      sendWebhook('page_view', {
        widgetLoaded: true,
        bubbleVisible: false,
        sessionData: sessionData,
        shouldTriggerAI: shouldTriggerAI(sessionData)
      });

      // Show bubble after delay
      setTimeout(() => {
        bubble.style.display = 'flex';
        sendWebhook('bubble_shown');
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
      
      // Real-time teaser message system
      if (finalConfig.analytics.console) {
        console.log('[AI PRL Assist] 🔍 Checking realTimeTeaser config:', finalConfig.realTimeTeaser);
      }
      
      if (finalConfig.realTimeTeaser?.enabled) {
        const pollInterval = finalConfig.realTimeTeaser.pollIntervalMs || 10000; // Default 10 seconds
        const apiKey = finalConfig.realTimeTeaser.apiKey;
        
        if (finalConfig.analytics.console) {
          console.log('[AI PRL Assist] 🚀 STARTING REAL-TIME TEASER POLLING!');
          console.log('[AI PRL Assist] Poll interval:', pollInterval + 'ms');
          console.log('[AI PRL Assist] API Key:', apiKey);
        }
        
        const pollForTeaserMessages = async () => {
          try {
            if (finalConfig.analytics.console) {
              console.log('[AI PRL Assist] 🔄 Polling for teaser messages...');
            }
            
            const { utmData, customData } = extractUrlData();
            
            const response = await fetch(`${finalConfig.apiBase || window.location.origin}/api/teaser-messages`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey,
                'X-Site-ID': siteId
              },
              body: JSON.stringify({
                siteId,
                sessionId: window.ChatWidget._sessionId,
                page: {
                  url: location.href,
                  pathname: location.pathname,
                  title: document.title
                },
                utm: utmData,
                custom: customData,
                timestamp: new Date().toISOString()
              })
            });
            
            if (response.ok) {
              const data = await response.json();
              if (finalConfig.analytics.console) {
                console.log('[AI PRL Assist] 📨 Polling response:', data);
              }
              
              if (data.message && data.message !== window.ChatWidget._lastTeaserMessage) {
                window.ChatWidget._lastTeaserMessage = data.message;
                
                if (finalConfig.analytics.console) {
                  console.log('[AI PRL Assist] 🎯 NEW TEASER MESSAGE RECEIVED:', data.message);
                }
                
                window.ChatWidget.showTeaser(data.message);
                
                sendWebhook('teaser_message_received', {
                  message: data.message,
                  source: 'external_ai'
                });
              } else if (finalConfig.analytics.console && !data.message) {
                console.log('[AI PRL Assist] 📭 No new teaser messages');
              }
            }
          } catch (error) {
            if (finalConfig.analytics.console) {
              console.warn('[AI PRL Assist] Teaser polling failed:', error);
            }
          }
        };
        
        // Start polling
        setInterval(pollForTeaserMessages, pollInterval);
        
        // Initial poll after 3 seconds
        setTimeout(pollForTeaserMessages, 3000);
      } else if (finalConfig.analytics.console) {
        console.log('[AI PRL Assist] ⚠️ Real-time teaser polling DISABLED or not configured');
      }

      // Mark as initialized
      window.ChatWidget._initialized = true;
      window.ChatWidget._initializing = false;
      
      if (finalConfig.analytics.console) {
        console.log('[AI PRL Assist] ✅ Widget initialization completed successfully!');
        console.log('[AI PRL Assist] Session ID:', window.ChatWidget._sessionId);
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
      // Pass full config including apiBase and analytics
      const setupConfig = {
        siteId: existingConfig.siteId,
        apiBase: existingConfig.apiBase || null,
        analytics: existingConfig.analytics?.console || false
      };
      
      if (existingConfig.analytics?.console) {
        console.log('[AI PRL Assist] 🚀 AUTO-INIT detected configuration:', setupConfig);
      }
      
      window.ChatWidget.setup(setupConfig);
      return;
    }
    
    // Fallback: Check URL params
    const urlParams = new URLSearchParams(window.location.search);
    const siteId = urlParams.get('siteId');
    if (siteId) {
      window.ChatWidget.setup({ siteId });
    }
  };
  
  // Try auto-init only once - wait a tick to ensure config is set
  setTimeout(() => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', autoInit);
    } else {
      autoInit();
    }
  }, 0);

})();


BUT 
