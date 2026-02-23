# Performance Optimization Guide for Odoo Frontend

## Core Web Vitals Optimization

### Largest Contentful Paint (LCP) < 2.5s

#### Image Optimization

```javascript
/** @odoo-module **/

export class ImageOptimizer {
    constructor() {
        this.supportedFormats = this.detectSupportedFormats();
    }

    detectSupportedFormats() {
        const formats = {
            webp: false,
            avif: false
        };

        // Detect WebP support
        const webP = new Image();
        webP.onload = webP.onerror = () => {
            formats.webp = webP.height === 2;
        };
        webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';

        // Detect AVIF support
        const avif = new Image();
        avif.onload = avif.onerror = () => {
            formats.avif = avif.height === 2;
        };
        avif.src = 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgANogQEAwgMg';

        return formats;
    }

    optimizeImageUrl(originalUrl, width, height) {
        const params = new URLSearchParams();

        // Add size parameters
        if (width) params.append('width', width);
        if (height) params.append('height', height);

        // Add format based on support
        if (this.supportedFormats.avif) {
            params.append('format', 'avif');
        } else if (this.supportedFormats.webp) {
            params.append('format', 'webp');
        }

        // Add quality parameter
        params.append('quality', '85');

        return `${originalUrl}?${params.toString()}`;
    }

    lazyLoadImages() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('fade-in');
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for older browsers
            document.querySelectorAll('img[data-src]').forEach(img => {
                img.src = img.dataset.src;
            });
        }
    }

    preloadCriticalImages() {
        // Preload hero image
        const heroImage = document.querySelector('.hero-image');
        if (heroImage) {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = heroImage.dataset.src;
            link.type = 'image/webp';
            document.head.appendChild(link);
        }

        // Preload above-the-fold images
        const criticalImages = document.querySelectorAll('.critical-image');
        criticalImages.forEach(img => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = img.dataset.src;
            document.head.appendChild(link);
        });
    }
}
```

#### Font Optimization

```css
/* Preload critical fonts */
@font-face {
    font-family: 'Inter';
    src: url('/fonts/inter.woff2') format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: swap; /* Prevent FOIT */
    size-adjust: 105%; /* Match fallback font metrics */
}

/* Use system fonts as fallback */
body {
    font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}
```

```xml
<!-- In QWeb template -->
<template id="font_preload" inherit_id="website.layout">
    <xpath expr="//head" position="inside">
        <link rel="preconnect" href="https://fonts.googleapis.com"/>
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
        <link rel="preload" as="font" type="font/woff2"
              href="/fonts/inter.woff2" crossorigin=""/>
    </xpath>
</template>
```

### First Input Delay (FID) / Interaction to Next Paint (INP) < 100ms

#### Code Splitting and Lazy Loading

```javascript
/** @odoo-module **/

export class CodeSplitter {
    constructor() {
        this.loadedModules = new Set();
    }

    async loadModule(moduleName) {
        if (this.loadedModules.has(moduleName)) {
            return;
        }

        try {
            const module = await import(
                /* webpackChunkName: "[request]" */
                `./modules/${moduleName}`
            );
            this.loadedModules.add(moduleName);
            return module.default;
        } catch (error) {
            console.error(`Failed to load module ${moduleName}:`, error);
        }
    }

    // Load heavy components on demand
    async loadHeavyComponent(componentName) {
        const module = await this.loadModule(componentName);
        if (module) {
            // Initialize component
            new module();
        }
    }

    // Defer non-critical scripts
    deferScript(src, callback) {
        const script = document.createElement('script');
        script.src = src;
        script.defer = true;
        script.onload = callback;
        document.body.appendChild(script);
    }
}
```

#### Debouncing and Throttling

```javascript
/** @odoo-module **/

export class PerformanceUtils {
    static debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    static requestIdleCallback(callback) {
        if ('requestIdleCallback' in window) {
            return window.requestIdleCallback(callback);
        }
        // Fallback
        return setTimeout(callback, 1);
    }

    static breakUpLongTask(items, processItem, chunkSize = 100) {
        return new Promise((resolve) => {
            const chunks = [];
            for (let i = 0; i < items.length; i += chunkSize) {
                chunks.push(items.slice(i, i + chunkSize));
            }

            let currentChunk = 0;

            function processNextChunk() {
                if (currentChunk < chunks.length) {
                    chunks[currentChunk].forEach(processItem);
                    currentChunk++;
                    this.requestIdleCallback(processNextChunk);
                } else {
                    resolve();
                }
            }

            processNextChunk();
        });
    }
}
```

### Cumulative Layout Shift (CLS) < 0.1

#### Reserve Space for Dynamic Content

```css
/* Reserve space for images */
.product-image-container {
    aspect-ratio: 1 / 1;
    background: #f0f0f0;
    contain: layout;
    overflow: hidden;
}

/* Reserve space for ads */
.ad-container {
    min-height: 250px;
    contain: layout style paint;
}

/* Prevent font loading shifts */
html {
    font-synthesis: none;
    text-rendering: optimizeLegibility;
}

/* Use CSS containment */
.product-card {
    contain: layout style paint;
    content-visibility: auto;
    contain-intrinsic-size: 0 300px;
}

/* Stable dimensions for dynamic content */
.skeleton-loader {
    min-height: 200px;
    animation: shimmer 2s infinite;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
```

#### Skeleton Screens

```javascript
/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";

export class ProductList extends Component {
    static template = xml`
        <div class="product-list">
            <t t-if="state.loading">
                <t t-foreach="[1, 2, 3, 4, 5, 6]" t-as="item" t-key="item">
                    <div class="product-skeleton">
                        <div class="skeleton-image"></div>
                        <div class="skeleton-text"></div>
                        <div class="skeleton-text short"></div>
                    </div>
                </t>
            </t>
            <t t-else="">
                <t t-foreach="state.products" t-as="product" t-key="product.id">
                    <ProductCard product="product"/>
                </t>
            </t>
        </div>
    `;

    setup() {
        this.state = useState({
            loading: true,
            products: []
        });

        onWillStart(async () => {
            await this.loadProducts();
        });
    }

    async loadProducts() {
        // Show skeleton while loading
        this.state.loading = true;

        const products = await this.rpc('/api/products');

        // Update with actual content
        this.state.products = products;
        this.state.loading = false;
    }
}
```

## Resource Optimization

### Critical CSS Extraction

```javascript
// build/extract-critical-css.js
const critical = require('critical');

critical.generate({
    inline: true,
    base: 'dist/',
    src: 'index.html',
    target: {
        html: 'index-critical.html',
        css: 'critical.css'
    },
    width: 1920,
    height: 1080,
    penthouse: {
        blockJSRequests: true,
        renderWaitTime: 100
    },
    extract: true,
    minify: true
});
```

### Resource Hints

```xml
<!-- Resource hints in QWeb template -->
<template id="resource_hints" inherit_id="website.layout">
    <xpath expr="//head" position="inside">
        <!-- DNS Prefetch for external domains -->
        <link rel="dns-prefetch" href="//cdn.jsdelivr.net"/>
        <link rel="dns-prefetch" href="//fonts.googleapis.com"/>
        <link rel="dns-prefetch" href="//www.google-analytics.com"/>

        <!-- Preconnect for critical origins -->
        <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin=""/>
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>

        <!-- Preload critical resources -->
        <link rel="preload" as="style" href="/web/assets/frontend.css"/>
        <link rel="preload" as="script" href="/web/assets/frontend.js"/>
        <link rel="preload" as="font" type="font/woff2"
              href="/fonts/inter.woff2" crossorigin=""/>

        <!-- Prefetch next page resources -->
        <link rel="prefetch" href="/shop/cart"/>
        <link rel="prefetch" as="image" href="/web/image/website/1/logo"/>

        <!-- Module preload for ES modules -->
        <link rel="modulepreload" href="/static/src/app.js"/>
    </xpath>
</template>
```

### Bundle Optimization

```javascript
// webpack.config.js or vite.config.js
export default {
    build: {
        rollupOptions: {
            output: {
                manualChunks(id) {
                    // Vendor chunk
                    if (id.includes('node_modules')) {
                        if (id.includes('owl')) {
                            return 'owl';
                        }
                        if (id.includes('bootstrap')) {
                            return 'bootstrap';
                        }
                        return 'vendor';
                    }
                    // Feature-based chunks
                    if (id.includes('/shop/')) {
                        return 'shop';
                    }
                    if (id.includes('/portal/')) {
                        return 'portal';
                    }
                },
                // Use content hash for cache busting
                entryFileNames: '[name].[hash].js',
                chunkFileNames: '[name].[hash].js',
                assetFileNames: '[name].[hash].[ext]'
            }
        },
        // Tree shaking
        treeshake: {
            moduleSideEffects: false,
            propertyReadSideEffects: false
        },
        // Minification
        minify: 'terser',
        terserOptions: {
            compress: {
                drop_console: true,
                drop_debugger: true,
                pure_funcs: ['console.log']
            },
            mangle: {
                safari10: true
            }
        }
    }
};
```

## Caching Strategies

### Browser Caching Headers

```python
# controllers/main.py
from odoo import http
from datetime import datetime, timedelta

class PerformanceController(http.Controller):

    @http.route('/web/assets/<string:filename>', type='http', auth='public')
    def serve_assets(self, filename):
        # Set aggressive caching for assets
        headers = [
            ('Cache-Control', 'public, max-age=31536000, immutable'),
            ('Expires', (datetime.now() + timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('ETag', self._generate_etag(filename))
        ]

        # Check if-none-match header
        if request.httprequest.headers.get('If-None-Match') == headers[2][1]:
            return Response(status=304)

        return request.make_response(
            self._get_asset_content(filename),
            headers=headers
        )

    def _generate_etag(self, filename):
        import hashlib
        return hashlib.md5(filename.encode()).hexdigest()
```

### Memory Caching

```javascript
/** @odoo-module **/

export class MemoryCache {
    constructor(maxSize = 100, ttl = 60000) {
        this.cache = new Map();
        this.maxSize = maxSize;
        this.ttl = ttl; // Time to live in ms
    }

    set(key, value) {
        // Implement LRU eviction
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }

        this.cache.set(key, {
            value,
            timestamp: Date.now()
        });
    }

    get(key) {
        const item = this.cache.get(key);

        if (!item) {
            return null;
        }

        // Check TTL
        if (Date.now() - item.timestamp > this.ttl) {
            this.cache.delete(key);
            return null;
        }

        // Move to end (LRU)
        this.cache.delete(key);
        this.cache.set(key, item);

        return item.value;
    }

    clear() {
        this.cache.clear();
    }

    // Decorator for caching function results
    static memoize(fn, ttl = 60000) {
        const cache = new MemoryCache(50, ttl);

        return async function(...args) {
            const key = JSON.stringify(args);
            const cached = cache.get(key);

            if (cached !== null) {
                return cached;
            }

            const result = await fn.apply(this, args);
            cache.set(key, result);
            return result;
        };
    }
}

// Usage
const fetchProducts = MemoryCache.memoize(async (category) => {
    return await rpc('/api/products', { category });
}, 300000); // Cache for 5 minutes
```

## Performance Monitoring

```javascript
/** @odoo-module **/

export class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }

    init() {
        this.measureCoreWebVitals();
        this.measureCustomMetrics();
        this.setupObservers();
    }

    measureCoreWebVitals() {
        // LCP
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            this.metrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
            this.reportMetric('LCP', this.metrics.lcp);
        }).observe({ type: 'largest-contentful-paint', buffered: true });

        // FID
        new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach(entry => {
                this.metrics.fid = entry.processingStart - entry.startTime;
                this.reportMetric('FID', this.metrics.fid);
            });
        }).observe({ type: 'first-input', buffered: true });

        // CLS
        let clsValue = 0;
        let clsEntries = [];
        let sessionValue = 0;
        let sessionEntries = [];

        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    const firstSessionEntry = sessionEntries[0];
                    const lastSessionEntry = sessionEntries[sessionEntries.length - 1];

                    if (sessionValue &&
                        entry.startTime - lastSessionEntry.startTime < 1000 &&
                        entry.startTime - firstSessionEntry.startTime < 5000) {
                        sessionValue += entry.value;
                        sessionEntries.push(entry);
                    } else {
                        sessionValue = entry.value;
                        sessionEntries = [entry];
                    }

                    if (sessionValue > clsValue) {
                        clsValue = sessionValue;
                        clsEntries = sessionEntries;
                        this.metrics.cls = clsValue;
                        this.reportMetric('CLS', clsValue);
                    }
                }
            }
        }).observe({ type: 'layout-shift', buffered: true });

        // INP (Interaction to Next Paint)
        let inpValue = 0;
        const processedInteractions = new Set();

        new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.interactionId && !processedInteractions.has(entry.interactionId)) {
                    processedInteractions.add(entry.interactionId);
                    inpValue = Math.max(inpValue, entry.duration);
                    this.metrics.inp = inpValue;
                    this.reportMetric('INP', inpValue);
                }
            }
        }).observe({ type: 'event', buffered: true, durationThreshold: 40 });
    }

    measureCustomMetrics() {
        // Time to Interactive
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            const tti = timing.domInteractive - timing.navigationStart;
            this.metrics.tti = tti;
            this.reportMetric('TTI', tti);
        }

        // JavaScript execution time
        const jsTime = performance.measure('js-exec', 'navigationStart', 'loadEventEnd');
        if (jsTime) {
            this.metrics.jsExecutionTime = jsTime.duration;
        }

        // Resource loading
        const resources = performance.getEntriesByType('resource');
        this.metrics.resources = {
            total: resources.length,
            size: resources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
            duration: Math.max(...resources.map(r => r.responseEnd))
        };
    }

    setupObservers() {
        // Long task observer
        if ('PerformanceObserver' in window) {
            new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.duration > 50) {
                        console.warn('Long task detected:', {
                            duration: entry.duration,
                            startTime: entry.startTime,
                            name: entry.name
                        });
                    }
                }
            }).observe({ entryTypes: ['longtask'] });
        }
    }

    reportMetric(name, value) {
        // Send to analytics
        if (window.gtag) {
            gtag('event', name, {
                value: Math.round(value),
                metric_id: name,
                page_path: window.location.pathname
            });
        }

        // Log to console in development
        if (process.env.NODE_ENV === 'development') {
            console.log(`Performance Metric - ${name}: ${value}`);
        }
    }

    getReport() {
        return {
            ...this.metrics,
            timestamp: Date.now(),
            url: window.location.href,
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            } : null
        };
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.performanceMonitor = new PerformanceMonitor();
});
```

## Best Practices

1. **Measure Before Optimizing**
   - Use Lighthouse for baseline metrics
   - Monitor Real User Metrics (RUM)
   - Set performance budgets

2. **Optimize Critical Path**
   - Inline critical CSS
   - Defer non-critical JavaScript
   - Preload key resources

3. **Image Optimization**
   - Use modern formats (WebP, AVIF)
   - Implement responsive images
   - Lazy load below-fold images

4. **Code Efficiency**
   - Remove unused CSS/JS
   - Minify and compress assets
   - Use tree shaking

5. **Caching Strategy**
   - Implement proper cache headers
   - Use service workers for offline
   - Version assets for cache busting

6. **Network Optimization**
   - Enable HTTP/2 or HTTP/3
   - Use CDN for static assets
   - Implement resource hints