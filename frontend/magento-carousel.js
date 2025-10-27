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

        return `
            <div class="function-result product-carousel">
                <div class="card-header">
                    <i class="fas fa-shopping-cart"></i>
                    <span>${title} (${products.length} items)</span>
                </div>
                <div class="carousel-container">
                    <div class="swiffy-slider slider-nav-round slider-nav-dark slider-item-show3 slider-item-show2-sm slider-item-show1-xs" id="${carouselId}">
                        <ul class="slider-container">
                            ${products.map(product => `<li>${this.createProductCard(product)}</li>`).join('')}
                        </ul>
                        <button type="button" class="slider-nav" onclick="woodstockCarousel.navigate('${carouselId}', 'prev')"></button>
                        <button type="button" class="slider-nav slider-nav-next" onclick="woodstockCarousel.navigate('${carouselId}', 'next')"></button>
                        <div class="slider-indicators"></div>
                    </div>
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
                         onload="console.log('✅ Image loaded:', this.src)"
                         onerror="console.log('❌ Image failed:', this.src); this.src='https://via.placeholder.com/300x200/002147/FFFFFF?text=Woodstock+Furniture'">
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
     * Initialize carousel with Swiffy Slider (BETTER, FASTER, MORE RELIABLE!)
     */
    initializeCarousel(carouselId) {
        // Load Swiffy Slider if not already loaded
        if (typeof window.swiffyslider === 'undefined') {
            this.loadSwiffySlider(() => {
                this.setupSwiffyCarousel(carouselId);
            });
        } else {
            this.setupSwiffyCarousel(carouselId);
        }
    }

    /**
     * Setup Swiffy Slider (much more reliable than Tiny Slider)
     */
    setupSwiffyCarousel(carouselId) {
        const sliderElement = document.getElementById(carouselId);
        if (!sliderElement) {
            console.error('❌ Swiffy Slider element not found:', carouselId);
            return;
        }

        console.log('🎨 Setting up Swiffy Slider:', carouselId);

        try {
            // Initialize this specific slider
            window.swiffyslider.initSlider(sliderElement);
            console.log('✅ Swiffy Slider initialized:', carouselId);
        } catch (error) {
            console.error('❌ Swiffy Slider setup error:', error);
        }
    }

    /**
     * Navigate Swiffy Slider programmatically
     */
    navigate(carouselId, direction) {
        const sliderElement = document.getElementById(carouselId);
        if (!sliderElement) {
            console.error('❌ Slider element not found for navigation:', carouselId);
            return;
        }

        console.log('🎯 Navigating Swiffy Slider:', carouselId, direction);
        
        try {
            if (window.swiffyslider) {
                const next = direction === 'next';
                // Use the correct Swiffy Slider navigation method
                window.swiffyslider.slide(sliderElement, next);
                console.log('✅ Navigation successful:', direction);
            } else {
                console.error('❌ Swiffy Slider not available for navigation');
            }
        } catch (error) {
            console.error('❌ Navigation error:', error);
        }
    }

    /**
     * Extract product image from Magento data
     */
    getProductImage(product) {
        console.log('🖼️ Extracting image for product:', product.name);
        console.log('🖼️ Product data:', {
            image_url: product.image_url,
            media_gallery_entries: product.media_gallery_entries?.length || 0,
            custom_attributes: product.custom_attributes?.length || 0
        });

        // PRIORITY 1: Use real image URL from backend (if provided)
        if (product.image_url && !product.image_url.includes('placeholder')) {
            console.log('✅ Using backend image_url:', product.image_url);
            return product.image_url;
        }
        
        // PRIORITY 2: Try media gallery entries (ORIGINAL WORKING PATTERN!)
        if (product.media_gallery_entries && product.media_gallery_entries.length > 0) {
            const mediaBase = 'https://www.woodstockoutlet.com/media/catalog/product';
            const imagePath = product.media_gallery_entries[0].file;
            const fullUrl = mediaBase + imagePath;
            console.log('✅ Using media gallery image:', fullUrl);
            return fullUrl;
        }
        
        // PRIORITY 3: Try custom attributes (ORIGINAL WORKING PATTERN!)
        if (product.custom_attributes) {
            const imageAttr = product.custom_attributes.find(attr => 
                attr.attribute_code === 'image' || attr.attribute_code === 'small_image'
            );
            if (imageAttr && imageAttr.value) {
                const fullUrl = 'https://www.woodstockoutlet.com/media/catalog/product' + imageAttr.value;
                console.log('✅ Using custom attribute image:', fullUrl);
                return fullUrl;
            }
        }

        // FALLBACK: High-quality furniture placeholder
        const productName = encodeURIComponent(product.name || 'Furniture');
        const fallbackUrl = `https://via.placeholder.com/400x300/002147/FFFFFF?text=${productName}`;
        console.log('⚠️ Using fallback placeholder:', fallbackUrl);
        return fallbackUrl;
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
     * Load Swiffy Slider library dynamically (MUCH BETTER than Tiny Slider!)
     */
    loadSwiffySlider(callback) {
        // Load CSS
        if (!document.querySelector('link[href*="swiffy-slider"]')) {
            const css = document.createElement('link');
            css.rel = 'stylesheet';
            css.href = 'https://cdn.jsdelivr.net/npm/swiffy-slider@1.6.0/dist/css/swiffy-slider.min.css';
            document.head.appendChild(css);
        }

        // Load JS
        if (!document.querySelector('script[src*="swiffy-slider"]')) {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/swiffy-slider@1.6.0/dist/js/swiffy-slider.min.js';
            script.setAttribute('defer', '');
            script.onload = () => {
                console.log('✅ Swiffy Slider loaded');
                if (callback) callback();
            };
            document.head.appendChild(script);
        } else {
            if (callback) callback();
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
