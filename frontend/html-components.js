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
                case 'getCustomerByPhone':
                case 'getCustomerByEmail':
                    return this.createCustomerCard(data);
                
                case 'getOrdersByCustomer':
                    return this.createOrdersList(data);
                
                case 'getDetailsByOrder':
                    return this.createOrderDetailsCard(data);
                
                case 'analyzeCustomerPatterns':
                    return this.createCustomerPatternsCard(data);
                
                case 'getProductRecommendations':
                    return this.createRecommendationsCard(data);
                
                case 'getCustomerJourney':
                    return this.createCustomerJourneyCard(data);
                
                case 'getCustomerAnalytics':
                    return this.createCustomerAnalyticsCard(data);
                
                case 'handleSupportEscalation':
                    return this.createSupportTicketCard(data);
                
                case 'handleLoyaltyUpgrade':
                    return this.createLoyaltyUpgradeCard(data);

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
            const total = parseFloat(order.ordertotal || 0).toFixed(2);
            
            return `
                <div class="order-item">
                    <div class="order-header">
                        <span class="order-id">#${order.orderid}</span>
                        <span class="order-status ${statusClass}">${this.getOrderStatusText(order.status)}</span>
                    </div>
                    <div class="order-details">
                        <div class="order-date">${this.formatDate(order.orderdate)}</div>
                        <div class="order-total">$${total}</div>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="function-result orders-list">
                <div class="card-header">
                    <i class="fas fa-shopping-bag"></i>
                    <span>Order History (${orders.length} orders)</span>
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
