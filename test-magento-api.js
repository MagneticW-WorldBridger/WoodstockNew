#!/usr/bin/env node

/**
 * 🔍 MAGENTO API IMAGE URL EXTRACTOR
 * Test direct Magento API calls to get real image URLs
 */

const https = require('https');

// Magento credentials (from original system)
const MAGENTO_USERNAME = 'jlasse@aiprlassist.com';
const MAGENTO_PASSWORD = 'bV38.O@3&/a{';
const MAGENTO_BASE = 'https://woodstockoutlet.com/rest';

async function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const req = https.request(url, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    resolve(data);
                }
            });
        });
        
        req.on('error', reject);
        
        if (options.body) {
            req.write(options.body);
        }
        
        req.end();
    });
}

async function getMagentoToken() {
    console.log('🔑 Getting Magento admin token...');
    
    try {
        const token = await makeRequest(`${MAGENTO_BASE}/all/V1/integration/admin/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: MAGENTO_USERNAME,
                password: MAGENTO_PASSWORD
            })
        });
        
        const cleanToken = token.replace(/"/g, '');
        console.log(`✅ Token obtained: ${cleanToken.substring(0, 20)}...`);
        return cleanToken;
        
    } catch (error) {
        console.error('❌ Token error:', error.message);
        return null;
    }
}

async function getProductsWithImages(token) {
    console.log('🛒 Getting products with image data...');
    
    try {
        const searchParams = new URLSearchParams({
            'searchCriteria[pageSize]': '5',
            'searchCriteria[currentPage]': '1',
            'searchCriteria[filterGroups][0][filters][0][field]': 'name',
            'searchCriteria[filterGroups][0][filters][0][value]': '%sectional%',
            'searchCriteria[filterGroups][0][filters][0][conditionType]': 'like',
            'searchCriteria[filterGroups][1][filters][0][field]': 'status',
            'searchCriteria[filterGroups][1][filters][0][value]': '2',
            'searchCriteria[filterGroups][1][filters][0][conditionType]': 'eq'
        });
        
        const url = `${MAGENTO_BASE}/V1/products?${searchParams.toString()}`;
        
        const data = await makeRequest(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (data.items) {
            console.log(`✅ Found ${data.items.length} products`);
            return data.items;
        } else {
            console.error('❌ No products found:', data);
            return [];
        }
        
    } catch (error) {
        console.error('❌ Product fetch error:', error.message);
        return [];
    }
}

async function extractImageUrls(products) {
    console.log('🖼️ Extracting image URLs from products...');
    
    const imageUrls = [];
    
    products.forEach((product, index) => {
        console.log(`\n📦 Product ${index + 1}: ${product.name}`);
        console.log(`   SKU: ${product.sku}`);
        
        // Extract from media_gallery_entries
        if (product.media_gallery_entries && product.media_gallery_entries.length > 0) {
            console.log(`   📸 Media gallery entries: ${product.media_gallery_entries.length}`);
            
            product.media_gallery_entries.forEach((entry, i) => {
                if (entry.file) {
                    const fullUrl = `https://woodstockoutlet.com/pub/media/catalog/product${entry.file}`;
                    console.log(`      ${i + 1}. ${fullUrl}`);
                    imageUrls.push({
                        product: product.name,
                        sku: product.sku,
                        source: 'media_gallery_entries',
                        url: fullUrl,
                        file: entry.file
                    });
                }
            });
        }
        
        // Extract from custom_attributes
        if (product.custom_attributes) {
            const imageAttrs = product.custom_attributes.filter(attr => 
                ['image', 'small_image', 'thumbnail', 'swatch_image'].includes(attr.attribute_code)
            );
            
            if (imageAttrs.length > 0) {
                console.log(`   🎨 Image attributes: ${imageAttrs.length}`);
                
                imageAttrs.forEach(attr => {
                    if (attr.value && attr.value !== 'no_selection') {
                        const fullUrl = `https://woodstockoutlet.com/pub/media/catalog/product${attr.value}`;
                        console.log(`      ${attr.attribute_code}: ${fullUrl}`);
                        imageUrls.push({
                            product: product.name,
                            sku: product.sku,
                            source: `custom_attribute_${attr.attribute_code}`,
                            url: fullUrl,
                            file: attr.value
                        });
                    }
                });
            }
        }
        
        if (!product.media_gallery_entries?.length && !product.custom_attributes?.some(attr => ['image', 'small_image'].includes(attr.attribute_code))) {
            console.log('   ⚠️ No image data found for this product');
        }
    });
    
    return imageUrls;
}

async function generateImageTestScript(imageUrls) {
    console.log('\n🚀 GENERATING IMAGE TEST SCRIPT...\n');
    
    console.log('📋 COPY/PASTE THIS INTO YOUR BROWSER CONSOLE:');
    console.log('=' * 60);
    
    const script = `
// 🖼️ MAGENTO IMAGE URL TESTER SCRIPT
const imageUrls = ${JSON.stringify(imageUrls, null, 2)};

console.log('🧪 Testing', imageUrls.length, 'image URLs...');

imageUrls.forEach((item, index) => {
    setTimeout(() => {
        console.log(\`🔍 Testing \${index + 1}/\${imageUrls.length}: \${item.product}\`);
        console.log(\`   URL: \${item.url}\`);
        window.open(item.url, \`_blank_\${index}\`);
    }, index * 500); // Open one every 500ms
});

console.log('✅ All image URLs will open in new tabs!');
    `;
    
    console.log(script);
    console.log('=' * 60);
    
    return script;
}

async function main() {
    console.log('🚀 STARTING MAGENTO IMAGE URL EXTRACTION...\n');
    
    try {
        // Step 1: Get admin token
        const token = await getMagentoToken();
        if (!token) {
            console.error('❌ Failed to get token, cannot continue');
            return;
        }
        
        // Step 2: Get products
        const products = await getProductsWithImages(token);
        if (products.length === 0) {
            console.error('❌ No products found, cannot extract images');
            return;
        }
        
        // Step 3: Extract image URLs
        const imageUrls = await extractImageUrls(products);
        
        console.log(`\n📊 SUMMARY:`);
        console.log(`   Products analyzed: ${products.length}`);
        console.log(`   Image URLs found: ${imageUrls.length}`);
        console.log(`   Sources: ${[...new Set(imageUrls.map(img => img.source))].join(', ')}`);
        
        // Step 4: Generate test script
        await generateImageTestScript(imageUrls);
        
        console.log('\n🎯 NEXT STEPS:');
        console.log('1. Copy the script above into your browser console');
        console.log('2. Run it to open all image URLs');
        console.log('3. Tell me which URLs show actual furniture images');
        console.log('4. I\'ll update the carousel to use the working pattern!');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    }
}

// Run the test
main().catch(console.error);
