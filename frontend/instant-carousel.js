/**
 * INSTANT CAROUSEL - No Delays, No Blinking!
 * Optimized carousel rendering that prevents delays and blinking
 */

class InstantCarousel {
    constructor() {
        console.log('🚀 InstantCarousel initialized - Zero delays!');
    }

    /**
     * Render carousel instantly without waiting for images
     */
    renderInstantCarousel(products, title = 'Products') {
        if (!products || products.length === 0) {
            return this.renderNoProducts();
        }

        const carouselId = `instant-carousel-${Date.now()}`;
        
        return `
            <div class="function-result product-carousel">
                <div class="card-header">
                    <i class="fas fa-shopping-cart"></i>
                    <span>${title} (${products.length} items)</span>
                </div>
                <div class="carousel-container">
                    <div class="swiffy-slider slider-nav-round slider-nav-dark slider-item-show3 slider-item-show2-sm slider-item-show1-xs" id="${carouselId}">
                        <ul class="slider-container">
                            ${products.map(product => `<li>${this.createInstantProductCard(product)}</li>`).join('')}
                        </ul>
                        <button type="button" class="slider-nav" onclick="instantCarousel.navigate('${carouselId}', 'prev')"></button>
                        <button type="button" class="slider-nav slider-nav-next" onclick="instantCarousel.navigate('${carouselId}', 'next')"></button>
                        <div class="slider-indicators"></div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create product card with instant rendering
     */
    createInstantProductCard(product) {
        const name = product.name || 'Product Name Not Available';
        const sku = product.sku || 'N/A';
        const price = this.formatPrice(product.price);
        const image = this.getOptimizedImage(product);
        const brand = this.extractBrand(product);
        const availability = product.status === 2 ? 'In Stock' : 'Out of Stock';
        const availabilityClass = product.status === 2 ? 'in-stock' : 'out-of-stock';

        return `
            <div class="product-card" data-sku="${sku}">
                <div class="product-image">
                    <img src="${image}" alt="${name}" loading="eager" 
                         onload="console.log('✅ Image loaded instantly:', this.src)"
                         onerror="console.log('❌ Image failed:', this.src); this.src='https://via.placeholder.com/400x300/002147/FFFFFF?text=Woodstock+Furniture'">
                    <div class="product-overlay">
                        <button class="quick-view-btn" onclick="instantCarousel.showProductDetails('${sku}')">
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
                        <button class="product-btn primary" onclick="instantCarousel.addToInterest('${sku}')">
                            <i class="fas fa-heart"></i>
                            Interested
                        </button>
                        <button class="product-btn secondary" onclick="instantCarousel.getMoreInfo('${sku}')">
                            <i class="fas fa-info-circle"></i>
                            Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get optimized image URL with instant fallback
     */
    getOptimizedImage(product) {
        // PRIORITY 1: Use backend image_url
        if (product.image_url && !product.image_url.includes('placeholder')) {
            return product.image_url;
        }
        
        // PRIORITY 2: Media gallery entries
        if (product.media_gallery_entries && product.media_gallery_entries.length > 0) {
            const mediaBase = 'https://www.woodstockoutlet.com/media/catalog/product';
            return mediaBase + product.media_gallery_entries[0].file;
        }
        
        // PRIORITY 3: Custom attributes
        if (product.custom_attributes) {
            const imageAttr = product.custom_attributes.find(attr => 
                attr.attribute_code === 'image' || attr.attribute_code === 'small_image'
            );
            if (imageAttr && imageAttr.value) {
                return 'https://www.woodstockoutlet.com/media/catalog/product' + imageAttr.value;
            }
        }

        // INSTANT FALLBACK: High-quality placeholder
        const productName = encodeURIComponent(product.name || 'Furniture');
        return `https://via.placeholder.com/400x300/002147/FFFFFF?text=${productName}`;
    }

    /**
     * Initialize Swiffy Slider instantly
     */
    initializeInstantly(carouselId) {
        const carouselEl = document.getElementById(carouselId);
        if (!carouselEl || !window.swiffyslider) {
            console.error('❌ Carousel element or Swiffy Slider not found');
            return;
        }

        console.log('🚀 INSTANT Swiffy Slider initialization for:', carouselId);
        
        try {
            // Initialize immediately - no waiting!
            window.swiffyslider.initSlider(carouselEl);
            console.log('✅ Swiffy Slider initialized INSTANTLY');
        } catch (error) {
            console.error('❌ Swiffy Slider initialization failed:', error);
        }
    }

    /**
     * Navigate carousel
     */
    navigate(carouselId, direction) {
        const sliderElement = document.getElementById(carouselId);
        if (!sliderElement || !window.swiffyslider) {
            console.error('❌ Slider element not found for navigation:', carouselId);
            return;
        }

        try {
            const next = direction === 'next';
            window.swiffyslider.slide(sliderElement, next);
            console.log('✅ Navigation successful:', direction);
        } catch (error) {
            console.error('❌ Navigation error:', error);
        }
    }

    /**
     * Format price
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
     * Extract brand
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
     * Render no products message
     */
    renderNoProducts() {
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

    /**
     * Product interaction handlers
     */
    showProductDetails(sku) {
        console.log('👁️ Showing details for product:', sku);
        alert(`Product details for ${sku} - This would open a beautiful modal!`);
    }

    addToInterest(sku) {
        console.log('❤️ Added to interest list:', sku);
        alert(`Added ${sku} to your interest list!`);
    }

    getMoreInfo(sku) {
        console.log('ℹ️ Getting more info for:', sku);
        if (window.woodstockChat) {
            window.woodstockChat.messageInput.value = `Tell me more about product ${sku}`;
            window.woodstockChat.handleSubmit(new Event('submit'));
        }
    }
}

// Initialize global instance
window.instantCarousel = new InstantCarousel();
