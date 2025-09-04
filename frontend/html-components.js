/**
 * WOODSTOCK FURNITURE - AMAZING HTML COMPONENTS
 * Ported from original system - Beautiful, rich UI components for function results
 */

class WoodstockComponents {
    constructor() {
        console.log('🎨 WoodstockComponents initialized - Amazing UI components ready!');
    }

    /**
     * Route function results to appropriate component renderers
     */
    renderFunctionResult(functionName, data) {
        console.log('🎨 Rendering function result:', functionName, data);

        try {
            switch (functionName) {
                // Core API Functions (4)
                case 'get_customer_by_phone':
                case 'getCustomerByPhone':
                case 'get_customer_by_email':
                case 'getCustomerByEmail':
                    return this.createCustomerCard(data);
                
                case 'get_orders_by_customer':
                case 'getOrdersByCustomer':
                    return this.createOrdersList(data);
                
                case 'get_order_details':
                case 'getDetailsByOrder':
                    return this.createOrderDetailsCard(data);
                
                // Analytics Functions (2)
                case 'analyze_customer_patterns':
                case 'analyzeCustomerPatterns':
                    return this.createCustomerPatternsCard(data);
                
                case 'get_customer_analytics':
                case 'getCustomerAnalytics':
                    return this.createCustomerAnalyticsCard(data);
                
                // Journey Function (1)
                case 'get_customer_journey':
                case 'getCustomerJourney':
                    return this.createCustomerJourneyCard(data);
                
                // Product Recommendation Functions (2) + Magento Search
                case 'get_product_recommendations':
                case 'getProductRecommendations':
                case 'handle_product_recommendations':
                case 'handleProductRecommendations':
                case 'search_magento_products':
                case 'searchMagentoProducts':
                    return this.createRecommendationsCard(data);
                
                // Proactive Functions (3)
                case 'handle_support_escalation':
                case 'handleSupportEscalation':
                    return this.createSupportTicketCard(data);
                
                case 'handle_loyalty_upgrade':
                case 'handleLoyaltyUpgrade':
                    return this.createLoyaltyUpgradeCard(data);
                
                case 'handle_order_confirmation_cross_sell':
                case 'handleOrderConfirmationCrossSell':
                    return this.createCrossSellCard(data);
                
                // Support Functions (2)
                case 'connect_to_support':
                case 'connectToSupport':
                    return this.createSupportConnectionCard(data);
                
                case 'show_directions':
                case 'showDirections':
                    return this.createDirectionsCard(data);

                // Google Calendar MCP functions
                case 'google_calendar-create-event':
                case 'google_calendar-quick-add-event':
                    return this.createCalendarEventCard(data);
                
                case 'google_calendar-list-events':
                    return this.createCalendarEventsListCard(data);

                default:
                    return this.createGenericCard(functionName, data);
            }
        } catch (error) {
            console.error('❌ Component rendering error:', error);
            return this.createErrorCard(functionName, error);
        }
    }

    /**
     * Customer Card Component - Beautiful customer profile
     */
    createCustomerCard(data) {
        if (!data.data || !data.data.entry || data.data.entry.length === 0) {
            return `<div class="function-result error">❌ Customer not found</div>`;
        }
        
        const customer = data.data.entry[0];
        const fullName = `${customer.firstname || ''} ${customer.lastname || ''}`.trim();
        const phone = customer.phonenumber || 'No phone';
        const email = customer.email || 'No email';
        const address = `${customer.address || ''}, ${customer.city || ''}, ${customer.state || ''} ${customer.zipcode || ''}`.replace(/^,\\s*|,\\s*$/, '');

        return `
            <div class="function-result customer-card">
                <div class="card-header">
                    <i class="fas fa-user-circle"></i>
                    <span>Customer Profile</span>
                </div>
                <div class="customer-info">
                    <div class="customer-name">${fullName || 'Name not available'}</div>
                    <div class="customer-details">
                        <div class="detail-item">
                            <i class="fas fa-phone"></i>
                            <span>${phone}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-envelope"></i>
                            <span>${email}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${address || 'Address not available'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Orders List Component - Beautiful order history
     */
    createOrdersList(data) {
        if (!data.data || !data.data.entry || data.data.entry.length === 0) {
            return `<div class="function-result error">❌ No orders found</div>`;
        }

        const orders = data.data.entry;
        const ordersHtml = orders.map(order => {
            const statusClass = this.getOrderStatusClass(order.status);
            const statusText = order.status_text || this.getOrderStatusText(order.status);
            const total = parseFloat(order.ordertotal || 0).toFixed(2);
            const orderDate = order.formatted_date || this.formatDate(order.orderdate);
            const deliveryDate = order.formatted_delivery || this.formatDate(order.deliverydate);
            
            return `
                <div class="order-item">
                    <div class="order-header">
                        <span class="order-id">#${order.orderid}</span>
                        <span class="order-status ${statusClass}">${statusText}</span>
                    </div>
                    <div class="order-details">
                        <div class="order-info">
                            <div class="order-date">
                                <i class="fas fa-calendar"></i>
                                <span>Ordered: ${orderDate}</span>
                            </div>
                            ${order.deliverydate && order.deliverydate !== 'N/A' ? `
                            <div class="delivery-date">
                                <i class="fas fa-truck"></i>
                                <span>Delivered: ${deliveryDate}</span>
                            </div>
                            ` : ''}
                        </div>
                        <div class="order-total">
                            <span class="total-label">Total:</span>
                            <span class="total-amount">$${total}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="function-result orders-list">
                <div class="card-header">
                    <i class="fas fa-shopping-bag"></i>
                    <span>Order History (${orders.length} order${orders.length > 1 ? 's' : ''})</span>
                </div>
                <div class="orders-container">
                    ${ordersHtml}
                </div>
            </div>
        `;
    }

    /**
     * Order Details Component - Detailed order breakdown
     */
    createOrderDetailsCard(data) {
        if (!data.data || !data.data.entry || data.data.entry.length === 0) {
            return `<div class="function-result error">❌ No order details found</div>`;
        }
        
        const items = data.data.entry;
        const itemsHtml = items.map(item => `
            <div class="order-line-item">
                <div class="item-info">
                    <div class="item-name">${item.description}</div>
                    <div class="item-id">Product ID: ${item.productid}</div>
                </div>
                <div class="item-details">
                    <div class="item-qty">Qty: ${parseFloat(item.qtyordered)}</div>
                    <div class="item-price">$${parseFloat(item.itemprice).toFixed(2)}</div>
                </div>
            </div>
        `).join('');
        
        const total = items.reduce((sum, item) => sum + (parseFloat(item.itemprice) * parseFloat(item.qtyordered)), 0);
        
        return `
            <div class="function-result order-details">
                <div class="card-header">
                    <i class="fas fa-list"></i>
                    <span>Order Details</span>
                </div>
                <div class="items-container">
                    ${itemsHtml}
                    <div class="order-total">
                        <strong>Total: $${total.toFixed(2)}</strong>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Customer Patterns Component - Analytics visualization
     */
    createCustomerPatternsCard(data) {
        const patterns = data.data || {};
        const totalSpent = parseFloat(patterns.totalSpent || 0).toFixed(2);
        const orderCount = patterns.orderCount || 0;
        const avgOrder = orderCount > 0 ? (parseFloat(patterns.totalSpent || 0) / orderCount).toFixed(2) : '0.00';
        const favoriteCategories = patterns.favoriteCategories || [];

        const categoriesHtml = favoriteCategories.slice(0, 5).map(category => `
            <div class="category-item">
                <span class="category-name">${category.category || 'Unknown'}</span>
                <span class="category-count">${category.count || 0} orders</span>
            </div>
        `).join('');

        return `
            <div class="function-result customer-patterns">
                <div class="card-header">
                    <i class="fas fa-chart-line"></i>
                    <span>Customer Patterns</span>
                </div>
                <div class="patterns-content">
                    <div class="patterns-stats">
                        <div class="stat-item">
                            <span class="stat-value">$${totalSpent}</span>
                            <span class="stat-label">Total Spent</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${orderCount}</span>
                            <span class="stat-label">Orders</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">$${avgOrder}</span>
                            <span class="stat-label">Avg Order</span>
                        </div>
                    </div>
                    <div class="favorite-categories">
                        <h4>Favorite Categories</h4>
                        <div class="categories-list">
                            ${categoriesHtml || '<div class="no-data">No category data available</div>'}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Calendar Event Component - Beautiful calendar event display
     */
    createCalendarEventCard(data) {
        const event = data.event || data;
        const title = event.title || event.summary || 'Calendar Event';
        const startTime = event.start ? this.formatDateTime(event.start) : 'TBD';
        const endTime = event.end ? this.formatDateTime(event.end) : 'TBD';
        const description = event.description || '';
        const location = event.location || '';

        return `
            <div class="function-result calendar-event">
                <div class="card-header">
                    <i class="fas fa-calendar-plus"></i>
                    <span>Appointment Scheduled</span>
                </div>
                <div class="event-content">
                    <div class="event-title">${title}</div>
                    <div class="event-details">
                        <div class="detail-item">
                            <i class="fas fa-clock"></i>
                            <span>${startTime} - ${endTime}</span>
                        </div>
                        ${location ? `
                        <div class="detail-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${location}</span>
                        </div>
                        ` : ''}
                        ${description ? `
                        <div class="detail-item">
                            <i class="fas fa-info-circle"></i>
                            <span>${description}</span>
                        </div>
                        ` : ''}
                    </div>
                    <div class="event-success">
                        ✅ Your appointment has been successfully scheduled!
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Support Ticket Component
     */
    createSupportTicketCard(data) {
        const ticket = data.data?.ticket || {};
        const ticketId = ticket.ticketId || 'GENERATED';
        const priority = ticket.priority || 'MEDIUM';
        const message = data.data?.message || 'Support request submitted';

        return `
            <div class="function-result support-ticket">
                <div class="card-header">
                    <i class="fas fa-headset"></i>
                    <span>Support Ticket Created</span>
                </div>
                <div class="ticket-info">
                    <div class="ticket-id">Ticket #${ticketId}</div>
                    <div class="ticket-priority priority-${priority.toLowerCase()}">${priority} Priority</div>
                    <div class="ticket-message">${message}</div>
                </div>
            </div>
        `;
    }

    /**
     * Customer Analytics Card Component
     */
    createCustomerAnalyticsCard(data) {
        const analytics = data.data || {};
        const totalSpent = parseFloat(analytics.totalSpent || 0).toFixed(2);
        const orderCount = analytics.orderCount || 0;
        const avgOrder = orderCount > 0 ? (parseFloat(analytics.totalSpent || 0) / orderCount).toFixed(2) : '0.00';

        return `
            <div class="function-result customer-analytics">
                <div class="card-header">
                    <i class="fas fa-chart-bar"></i>
                    <span>Customer Analytics</span>
                </div>
                <div class="analytics-content">
                    <div class="analytics-stats">
                        <div class="stat-item">
                            <span class="stat-value">$${totalSpent}</span>
                            <span class="stat-label">Lifetime Value</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${orderCount}</span>
                            <span class="stat-label">Total Orders</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">$${avgOrder}</span>
                            <span class="stat-label">Average Order</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Cross-Sell Card Component
     */
    createCrossSellCard(data) {
        const crossSell = data.data || {};
        const recommendations = crossSell.recommendations || [];

        const recsHtml = recommendations.slice(0, 3).map(rec => `
            <div class="cross-sell-item">
                <div class="rec-name">${rec.name || 'Product'}</div>
                <div class="rec-price">$${rec.price || '0.00'}</div>
            </div>
        `).join('');

        return `
            <div class="function-result cross-sell">
                <div class="card-header">
                    <i class="fas fa-shopping-cart"></i>
                    <span>Recommended for You</span>
                </div>
                <div class="cross-sell-content">
                    <div class="cross-sell-message">${crossSell.message || 'Based on your purchase, you might like:'}</div>
                    <div class="recommendations-list">
                        ${recsHtml || '<div class="no-data">No recommendations available</div>'}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Support Connection Card Component
     */
    createSupportConnectionCard(data) {
        const support = data.data || {};
        const ticketId = support.ticketId || 'SUPPORT-' + Date.now();

        return `
            <div class="function-result support-connection">
                <div class="card-header">
                    <i class="fas fa-phone"></i>
                    <span>Human Support Connected</span>
                </div>
                <div class="support-content">
                    <div class="connection-info">
                        <div class="support-id">Reference: ${ticketId}</div>
                        <div class="support-message">A support specialist will contact you shortly.</div>
                    </div>
                    <div class="contact-options">
                        <div class="contact-item">
                            <i class="fas fa-phone"></i>
                            <span>1-800-WOODSTOCK</span>
                        </div>
                        <div class="contact-item">
                            <i class="fas fa-envelope"></i>
                            <span>support@woodstockoutlet.com</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Directions Card Component
     */
    createDirectionsCard(data) {
        const directions = data.data || {};
        const storeName = directions.storeName || 'Woodstock Furniture Store';
        const address = directions.address || 'Store location';

        return `
            <div class="function-result directions">
                <div class="card-header">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>Directions</span>
                </div>
                <div class="directions-content">
                    <div class="store-info">
                        <div class="store-name">${storeName}</div>
                        <div class="store-address">${address}</div>
                    </div>
                    <div class="directions-actions">
                        <a href="#" class="directions-btn" onclick="window.open('https://maps.google.com/maps?q=${encodeURIComponent(address)}', '_blank')">
                            <i class="fas fa-external-link-alt"></i>
                            Open in Google Maps
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Recommendations Card Component
     */
    createRecommendationsCard(data) {
        console.log('🎨 createRecommendationsCard called with:', data);
        
        const recommendations = data.data || {};
        const products = recommendations.products || [];

        console.log('🛒 Products found:', products.length);

        // FORCE CAROUSEL RENDERING
        if (products.length > 0) {
            console.log('🎨 Rendering carousel with products:', products);
            
            if (window.woodstockCarousel) {
                const carouselHTML = window.woodstockCarousel.createProductCarousel(products, 'Sectional Products');
                console.log('🎨 Carousel HTML generated:', carouselHTML.substring(0, 100) + '...');
                return carouselHTML;
            } else {
                console.error('❌ woodstockCarousel not available!');
            }
        }

        // Enhanced fallback with product cards
        const productsHtml = products.slice(0, 4).map(product => `
            <div class="product-card-simple">
                <div class="product-name">${product.name || 'Product'}</div>
                <div class="product-sku">SKU: ${product.sku || 'N/A'}</div>
                <div class="product-price">$${(product.price || 0).toLocaleString()}</div>
                <div class="product-status">● In Stock</div>
            </div>
        `).join('');

        return `
            <div class="function-result recommendations">
                <div class="card-header">
                    <i class="fas fa-shopping-cart"></i>
                    <span>Sectional Products (${products.length} found)</span>
                </div>
                <div class="recommendations-content">
                    <div class="products-grid">
                        ${productsHtml || '<div class="no-data">No products available at this time</div>'}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Customer Journey Card Component  
     */
    createCustomerJourneyCard(data) {
        const journey = data.data || {};
        const customer = journey.customer || {};
        const orders = journey.orders || [];

        const ordersHtml = orders.map(order => `
            <div class="journey-order">
                <div class="journey-order-header">
                    <span class="journey-order-id">#${order.orderid}</span>
                    <span class="journey-order-date">${this.formatDate(order.orderdate)}</span>
                </div>
                <div class="journey-order-total">$${parseFloat(order.ordertotal || 0).toFixed(2)}</div>
            </div>
        `).join('');

        return `
            <div class="function-result customer-journey">
                <div class="card-header">
                    <i class="fas fa-route"></i>
                    <span>Customer Journey</span>
                </div>
                <div class="journey-content">
                    <div class="journey-summary">
                        <div class="customer-name">${customer.firstname || ''} ${customer.lastname || ''}</div>
                        <div class="journey-stats">
                            <div class="stat-item">
                                <span class="stat-value">${orders.length}</span>
                                <span class="stat-label">Orders</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-value">$${journey.totalSpent || '0.00'}</span>
                                <span class="stat-label">Total Spent</span>
                            </div>
                        </div>
                    </div>
                    <div class="journey-orders">
                        <h4>Order Timeline</h4>
                        <div class="journey-orders-list">
                            ${ordersHtml || '<div class="no-data">No order history available</div>'}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Loyalty Upgrade Card Component
     */
    createLoyaltyUpgradeCard(data) {
        const loyalty = data.data || {};
        const status = loyalty.status || 'Bronze';
        const message = loyalty.message || 'Loyalty program information';

        return `
            <div class="function-result loyalty-upgrade">
                <div class="card-header">
                    <i class="fas fa-crown"></i>
                    <span>Loyalty Program</span>
                </div>
                <div class="loyalty-content">
                    <div class="loyalty-status">
                        <div class="status-badge status-${status.toLowerCase()}">${status} Member</div>
                        <div class="loyalty-message">${message}</div>
                    </div>
                    <div class="loyalty-benefits">
                        <div class="benefit-item">
                            <i class="fas fa-gift"></i>
                            <span>Exclusive member discounts</span>
                        </div>
                        <div class="benefit-item">
                            <i class="fas fa-shipping-fast"></i>
                            <span>Free shipping on orders over $500</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Generic Card for unknown function results
     */
    createGenericCard(functionName, data) {
        return `
            <div class="function-result generic-card">
                <div class="card-header">
                    <i class="fas fa-cog"></i>
                    <span>${functionName}</span>
                </div>
                <div class="generic-content">
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            </div>
        `;
    }

    /**
     * Error Card for rendering failures
     */
    createErrorCard(functionName, error) {
        return `
            <div class="function-result error-card">
                <div class="card-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Component Error</span>
                </div>
                <div class="error-content">
                    <div class="error-function">Function: ${functionName}</div>
                    <div class="error-message">Error: ${error.message}</div>
                </div>
            </div>
        `;
    }

    // Helper methods
    getOrderStatusClass(status) {
        const statusMap = {
            'F': 'status-finalized',
            'P': 'status-pending', 
            'C': 'status-cancelled',
            'S': 'status-shipped'
        };
        return statusMap[status] || 'status-unknown';
    }

    getOrderStatusText(status) {
        const statusMap = {
            'F': 'Finalized',
            'P': 'Pending',
            'C': 'Cancelled', 
            'S': 'Shipped'
        };
        return statusMap[status] || 'Unknown';
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
    }

    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        } catch {
            return dateString;
        }
    }
}

// Initialize global instance
window.woodstockComponents = new WoodstockComponents();
