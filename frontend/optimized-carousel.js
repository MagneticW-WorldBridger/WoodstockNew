/**
 * OPTIMIZED CAROUSEL - Zero Delays, Perfect Performance
 * Replaces the complex carousel logic with instant rendering
 */

// Override the carousel rendering in the main script
window.optimizedCarousel = {
    renderCarousel: function(products, title) {
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

        const carouselId = `optimized-carousel-${Date.now()}`;
        
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
                        <button type="button" class="slider-nav" onclick="optimizedCarousel.navigate('${carouselId}', 'prev')"></button>
                        <button type="button" class="slider-nav slider-nav-next" onclick="optimizedCarousel.navigate('${carouselId}', 'next')"></button>
                        <div class="slider-indicators"></div>
                    </div>
                </div>
            </div>
        `;
    },

    createProductCard: function(product) {
        const name = product.name || 'Product Name Not Available';
        const sku = product.sku || 'N/A';
        const price = this.formatPrice(product.price);
        const image = this.getImage(product);
        const brand = 'Woodstock Furniture';
        const availability = product.status === 2 ? 'In Stock' : 'Out of Stock';
        const availabilityClass = product.status === 2 ? 'in-stock' : 'out-of-stock';

        return `
            <div class="product-card" data-sku="${sku}">
                <div class="product-image">
                    <img src="${image}" alt="${name}" loading="eager">
                    <div class="product-overlay">
                        <button class="quick-view-btn" onclick="optimizedCarousel.showProductDetails('${sku}')">
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
                        <button class="product-btn primary" onclick="optimizedCarousel.addToInterest('${sku}')">
                            <i class="fas fa-heart"></i>
                            Interested
                        </button>
                        <button class="product-btn secondary" onclick="optimizedCarousel.getMoreInfo('${sku}')">
                            <i class="fas fa-info-circle"></i>
                            Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    getImage: function(product) {
        // Use backend image_url if available
        if (product.image_url && !product.image_url.includes('placeholder')) {
            return product.image_url;
        }
        
        // Try media gallery entries
        if (product.media_gallery_entries && product.media_gallery_entries.length > 0) {
            return 'https://www.woodstockoutlet.com/media/catalog/product' + product.media_gallery_entries[0].file;
        }
        
        // Try custom attributes
        if (product.custom_attributes) {
            const imageAttr = product.custom_attributes.find(attr => 
                attr.attribute_code === 'image' || attr.attribute_code === 'small_image'
            );
            if (imageAttr && imageAttr.value) {
                return 'https://www.woodstockoutlet.com/media/catalog/product' + imageAttr.value;
            }
        }

        // Fallback placeholder
        const productName = encodeURIComponent(product.name || 'Furniture');
        return `https://via.placeholder.com/400x300/002147/FFFFFF?text=${productName}`;
    },

    formatPrice: function(price) {
        if (!price || price === 0) return 'Price on Request';
        
        const numPrice = parseFloat(price);
        if (isNaN(numPrice)) return 'Price on Request';
        
        return '$' + numPrice.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    },

    initializeInstantly: function(carouselId) {
        const carouselEl = document.getElementById(carouselId);
        if (!carouselEl || !window.swiffyslider) {
            console.error('❌ Carousel element or Swiffy Slider not found');
            return;
        }

        console.log('🚀 INSTANT Swiffy Slider initialization for:', carouselId);
        
        try {
            window.swiffyslider.initSlider(carouselEl);
            console.log('✅ Swiffy Slider initialized INSTANTLY');
        } catch (error) {
            console.error('❌ Swiffy Slider initialization failed:', error);
        }
    },

    navigate: function(carouselId, direction) {
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
    },

    showProductDetails: function(sku) {
        console.log('👁️ Showing details for product:', sku);
        alert(`Product details for ${sku} - This would open a beautiful modal!`);
    },

    addToInterest: function(sku) {
        console.log('❤️ Added to interest list:', sku);
        alert(`Added ${sku} to your interest list!`);
    },

    getMoreInfo: function(sku) {
        console.log('ℹ️ Getting more info for:', sku);
        if (window.woodstockChat) {
            window.woodstockChat.messageInput.value = `Tell me more about product ${sku}`;
            window.woodstockChat.handleSubmit(new Event('submit'));
        }
    }
};
