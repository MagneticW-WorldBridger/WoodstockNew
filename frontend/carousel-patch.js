/**
 * CAROUSEL PATCH - Fix blinking and delays
 * This script patches the carousel rendering to prevent delays and blinking
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Carousel patch loaded - fixing blinking issues');
    
    // Override the carousel rendering in the main script
    if (window.woodstockChat && window.woodstockChat.detectAndRenderComponents) {
        const originalDetectAndRenderComponents = window.woodstockChat.detectAndRenderComponents;
        
        window.woodstockChat.detectAndRenderComponents = function(fullResponse, contentDiv) {
            // Check for CAROUSEL_DATA first (Magento products)
            if (fullResponse.includes('CAROUSEL_DATA:')) {
                console.log('🛒 PRIORITY: CAROUSEL_DATA detected - using OPTIMIZED rendering');
                
                // Extract JSON data
                const startMarker = '**CAROUSEL_DATA:**';
                const startIndex = fullResponse.indexOf(startMarker);
                
                if (startIndex !== -1) {
                    let jsonStart = fullResponse.indexOf('{', startIndex);
                    
                    if (jsonStart !== -1) {
                        let braceCount = 0;
                        let jsonEnd = jsonStart;
                        
                        for (let i = jsonStart; i < fullResponse.length; i++) {
                            if (fullResponse[i] === '{') braceCount++;
                            if (fullResponse[i] === '}') braceCount--;
                            
                            if (braceCount === 0) {
                                jsonEnd = i + 1;
                                break;
                            }
                        }
                        
                        const jsonString = fullResponse.substring(jsonStart, jsonEnd);
                        
                        try {
                            const carouselData = JSON.parse(jsonString);
                            console.log('✅ Parsed carousel data - products:', carouselData.products?.length || 0);
                            
                            // Use OPTIMIZED carousel rendering
                            if (window.optimizedCarousel && carouselData.products && carouselData.products.length > 0) {
                                console.log('🚀 OPTIMIZED carousel rendering - NO DELAYS!');
                                const carouselHTML = window.optimizedCarousel.renderCarousel(
                                    carouselData.products, 
                                    `Found ${carouselData.products.length} Products`
                                );
                                contentDiv.innerHTML = carouselHTML;
                                
                                // INSTANT Swiffy Slider initialization
                                setTimeout(() => {
                                    const carouselEl = contentDiv.querySelector('[id^="optimized-carousel-"]');
                                    if (carouselEl) {
                                        console.log('🚀 INSTANT Swiffy Slider initialization for:', carouselEl.id);
                                        window.optimizedCarousel.initializeInstantly(carouselEl.id);
                                    } else {
                                        console.error('❌ Optimized carousel element not found');
                                    }
                                }, 10); // Ultra-fast initialization
                                return;
                            } else {
                                console.error('❌ optimizedCarousel not available or no products');
                            }
                        } catch (error) {
                            console.error('❌ CAROUSEL_DATA JSON parsing failed:', error);
                        }
                    }
                }
            }
            
            // Fall back to original method for non-carousel content
            return originalDetectAndRenderComponents.call(this, fullResponse, contentDiv);
        };
        
        console.log('✅ Carousel patch applied successfully');
    } else {
        console.error('❌ Could not apply carousel patch - woodstockChat not found');
    }
});
