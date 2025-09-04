/**
 * WOODSTOCK FURNITURE - MAGENTO PRODUCT CAROUSEL
 * Based on Tiny Slider + Magento REST API integration
 * Convergent wisdom from Context7 and Brave Search
 */

class WoodstockMagentoCarousel {
    constructor() {
        this.apiBase = 'https://woodstockoutlet.com/rest/V1';
        this.authToken = null; // Will be set when needed
        console.log('🎨 WoodstockMagentoCarousel initialized - Ready for product displays!');
    }

    /**
     * Create beautiful product carousel from Magento API data
     */
    createProductCarousel(products, title = 'Recommended Products') {
        if (!products || products.length === 0) {
            return `
                <div class="function-result product-carousel">
                    <div class="card-header">
                        <i class="fas fa-shopping-cart"></i>
                        <span>No Products Found</span>
                    </div>
                    <div class="no-products">
                        <i class="fas fa-search" style="font-size: 3rem; color: var(--woodstock-red); opacity: 0.3;"></i>
                        <p>No products available at this time</p>
                    </div>
                </div>
            `;
        }

        const carouselId = `carousel-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        const productsHtml = products.map(product => this.createProductCard(product)).join('');

        // Auto-initialize carousel after render
        setTimeout(() => {
            this.initializeCarousel(carouselId);
        }, 100);

        return `
            <div class="function-result product-carousel">
                <div class="card-header">
                    <i class="fas fa-shopping-cart"></i>
                    <span>${title} (${products.length} items)</span>
                </div>
                <div class="carousel-container">
                    <div class="carousel-controls">
                        <button class="carousel-btn prev-btn" onclick="woodstockCarousel.navigate('${carouselId}', 'prev')">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        <button class="carousel-btn next-btn" onclick="woodstockCarousel.navigate('${carouselId}', 'next')">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                    <div class="product-carousel-wrapper" id="${carouselId}">
                        <div class="product-carousel-track">
                            ${productsHtml}
                        </div>
                    </div>
                    <div class="carousel-dots" id="${carouselId}-dots"></div>
                </div>
            </div>
        `;
    }

    /**
     * Create individual product card with Woodstock styling
     */
    createProductCard(product) {
        const name = product.name || 'Product Name Not Available';
        const sku = product.sku || 'N/A';
        const price = this.formatPrice(product.price);
        const image = this.getProductImage(product);
        const brand = this.extractBrand(product);
        const availability = product.status === 2 ? 'In Stock' : 'Out of Stock';
        const availabilityClass = product.status === 2 ? 'in-stock' : 'out-of-stock';

        return `
            <div class="product-card" data-sku="${sku}">
                <div class="product-image">
                    <img src="${image}" alt="${name}" loading="lazy" 
                         onerror="this.src='https://via.placeholder.com/300x200/002147/FFFFFF?text=Woodstock+Furniture'">
                    <div class="product-overlay">
                        <button class="quick-view-btn" onclick="woodstockCarousel.showProductDetails('${sku}')">
                            <i class="fas fa-eye"></i>
                            Quick View
                        </button>
                    </div>
                </div>
                <div class="product-info">
                    <div class="product-brand">${brand}</div>
                    <div class="product-name">${name}</div>
                    <div class="product-price">${price}</div>
                    <div class="product-availability ${availabilityClass}">
                        <i class="fas fa-circle"></i>
                        <span>${availability}</span>
                    </div>
                    <div class="product-actions">
                        <button class="product-btn primary" onclick="woodstockCarousel.addToInterest('${sku}')">
                            <i class="fas fa-heart"></i>
                            Interested
                        </button>
                        <button class="product-btn secondary" onclick="woodstockCarousel.getMoreInfo('${sku}')">
                            <i class="fas fa-info-circle"></i>
                            Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Initialize carousel with Tiny Slider (responsive, touch-friendly)
     */
    initializeCarousel(carouselId) {
        // Load Tiny Slider if not already loaded
        if (typeof tns === 'undefined') {
            this.loadTinySlider(() => {
                this.setupCarousel(carouselId);
            });
        } else {
            this.setupCarousel(carouselId);
        }
    }

    /**
     * Setup carousel with responsive configuration
     */
    setupCarousel(carouselId) {
        const container = document.querySelector(`#${carouselId} .product-carousel-track`);
        if (!container) return;

        const slider = tns({
            container: container,
            items: 1,
            slideBy: 'page',
            mouseDrag: true,
            touch: true,
            controls: false, // We have custom controls
            nav: true,
            navContainer: `#${carouselId}-dots`,
            // FIXED: Enable wheel/trackpad scrolling
            swipeAngle: 15,
            preventActionWhenRunning: false,
            preventScrollOnTouch: 'auto',
            nested: false,
            freezable: true,
            responsive: {
                480: {
                    items: 2,
                    gutter: 10,
                    slideBy: 1
                },
                768: {
                    items: 3,
                    gutter: 15,
                    slideBy: 1
                },
                1024: {
                    items: 4,
                    gutter: 20,
                    slideBy: 1
                }
            },
            autoplay: false,
            speed: 300,
            autoHeight: false,
            loop: false,
            rewind: true
        });

        // ADD WHEEL/TRACKPAD SUPPORT
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            if (e.deltaX > 0 || e.deltaY > 0) {
                slider.goTo('next');
            } else {
                slider.goTo('prev');
            }
        }, { passive: false });

        // Store slider instance for navigation
        this.sliders = this.sliders || {};
        this.sliders[carouselId] = slider;
    }

    /**
     * Navigate carousel programmatically
     */
    navigate(carouselId, direction) {
        const slider = this.sliders && this.sliders[carouselId];
        if (!slider) return;

        if (direction === 'next') {
            slider.goTo('next');
        } else if (direction === 'prev') {
            slider.goTo('prev');
        }
    }

    /**
     * Extract product image from Magento data
     */
    getProductImage(product) {
        // Try various image sources from Magento
        if (product.media_gallery_entries && product.media_gallery_entries.length > 0) {
            const mediaBase = 'https://woodstockoutlet.com/pub/media/catalog/product';
            return mediaBase + product.media_gallery_entries[0].file;
        }
        
        if (product.custom_attributes) {
            const imageAttr = product.custom_attributes.find(attr => 
                attr.attribute_code === 'image' || attr.attribute_code === 'small_image'
            );
            if (imageAttr && imageAttr.value) {
                return 'https://woodstockoutlet.com/pub/media/catalog/product' + imageAttr.value;
            }
        }

        // Fallback to Woodstock branded placeholder
        return 'https://via.placeholder.com/300x200/002147/FFFFFF?text=Woodstock+Furniture';
    }

    /**
     * Extract brand from Magento product data
     */
    extractBrand(product) {
        if (product.custom_attributes) {
            const brandAttr = product.custom_attributes.find(attr => 
                attr.attribute_code === 'brand' || attr.attribute_code === 'manufacturer'
            );
            if (brandAttr && brandAttr.value) {
                return brandAttr.value;
            }
        }
        return 'Woodstock Furniture';
    }

    /**
     * Format price with proper currency
     */
    formatPrice(price) {
        if (!price || price === 0) return 'Price on Request';
        
        const numPrice = parseFloat(price);
        if (isNaN(numPrice)) return 'Price on Request';
        
        return '$' + numPrice.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    /**
     * Load Tiny Slider library dynamically
     */
    loadTinySlider(callback) {
        // Load CSS
        if (!document.querySelector('link[href*="tiny-slider"]')) {
            const css = document.createElement('link');
            css.rel = 'stylesheet';
            css.href = 'https://cdnjs.cloudflare.com/ajax/libs/tiny-slider/2.9.4/tiny-slider.css';
            document.head.appendChild(css);
        }

        // Load JS
        if (!document.querySelector('script[src*="tiny-slider"]')) {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/tiny-slider/2.9.4/min/tiny-slider.js';
            script.onload = callback;
            document.head.appendChild(script);
        } else {
            callback();
        }
    }

    /**
     * Product interaction handlers
     */
    showProductDetails(sku) {
        console.log('👁️ Showing details for product:', sku);
        // This could trigger a modal or detailed view
        alert(`Product details for ${sku} - This would open a beautiful modal!`);
    }

    addToInterest(sku) {
        console.log('❤️ Added to interest list:', sku);
        // This could save to localStorage or send to backend
        alert(`Added ${sku} to your interest list!`);
    }

    getMoreInfo(sku) {
        console.log('ℹ️ Getting more info for:', sku);
        // This could trigger an AI query about the specific product
        if (window.woodstockChat) {
            window.woodstockChat.messageInput.value = `Tell me more about product ${sku}`;
            window.woodstockChat.handleSubmit(new Event('submit'));
        }
    }
}

// Initialize global carousel instance
window.woodstockCarousel = new WoodstockMagentoCarousel();
