# Progressive Web App (PWA) Patterns for Odoo

## Overview

Transform your Odoo website into a Progressive Web App with offline support, push notifications, and app-like experience.

## Service Worker Implementation

### Basic Service Worker

```javascript
// static/src/service-worker.js
const CACHE_NAME = 'odoo-pwa-v1';
const urlsToCache = [
  '/',
  '/web/static/lib/owl/owl.js',
  '/web/static/src/legacy/js/public/public_root.js',
  '/web/static/src/libs/fontawesome/css/font-awesome.css',
];

// Install event - cache essential resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        // Clone the request
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then(response => {
          // Check if we received a valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });

          return response;
        });
      })
      .catch(() => {
        // Offline fallback
        return caches.match('/offline.html');
      })
  );
});

// Activate event - clean old caches
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];

  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Claim all clients
  self.clients.claim();
});
```

### Advanced Caching Strategies

```javascript
// Network First Strategy (for API calls)
function networkFirst(request) {
  return fetch(request)
    .then(response => {
      const responseClone = response.clone();
      caches.open(CACHE_NAME).then(cache => {
        cache.put(request, responseClone);
      });
      return response;
    })
    .catch(() => {
      return caches.match(request);
    });
}

// Cache First Strategy (for static assets)
function cacheFirst(request) {
  return caches.match(request)
    .then(response => {
      if (response) {
        return response;
      }
      return fetch(request).then(response => {
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(request, responseClone);
        });
        return response;
      });
    });
}

// Stale While Revalidate
function staleWhileRevalidate(request) {
  return caches.match(request).then(cachedResponse => {
    const fetchPromise = fetch(request).then(networkResponse => {
      caches.open(CACHE_NAME).then(cache => {
        cache.put(request, networkResponse.clone());
      });
      return networkResponse;
    });
    return cachedResponse || fetchPromise;
  });
}

// Apply strategies based on request type
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // API calls - network first
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Static assets - cache first
  if (request.destination === 'image' ||
      request.destination === 'style' ||
      request.destination === 'script') {
    event.respondWith(cacheFirst(request));
    return;
  }

  // HTML pages - stale while revalidate
  if (request.mode === 'navigate') {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Default
  event.respondWith(fetch(request));
});
```

## Web App Manifest

### Complete Manifest Configuration

```json
// static/src/manifest.json
{
  "name": "Odoo Progressive Web Application",
  "short_name": "OdooPWA",
  "description": "Odoo ERP as a Progressive Web Application",
  "start_url": "/?utm_source=pwa",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "background_color": "#875A7B",
  "theme_color": "#875A7B",
  "dir": "ltr",
  "lang": "en-US",
  "categories": ["business", "productivity"],
  "icons": [
    {
      "src": "/web/static/img/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/web/static/img/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/web/static/img/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/web/static/img/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/web/static/img/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/web/static/img/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/web/static/img/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/web/static/img/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/web/static/img/screenshots/desktop.png",
      "sizes": "1920x1080",
      "type": "image/png"
    },
    {
      "src": "/web/static/img/screenshots/mobile.png",
      "sizes": "750x1334",
      "type": "image/png"
    }
  ],
  "shortcuts": [
    {
      "name": "Shop",
      "url": "/shop",
      "icons": [{
        "src": "/web/static/img/icons/shop.png",
        "sizes": "96x96"
      }]
    },
    {
      "name": "My Account",
      "url": "/my",
      "icons": [{
        "src": "/web/static/img/icons/account.png",
        "sizes": "96x96"
      }]
    }
  ],
  "related_applications": [],
  "prefer_related_applications": false
}
```

### Link Manifest in QWeb Template

```xml
<!-- views/templates.xml -->
<template id="pwa_meta_tags" inherit_id="website.layout">
    <xpath expr="//head" position="inside">
        <!-- Web App Manifest -->
        <link rel="manifest" href="/manifest.json"/>

        <!-- iOS Support -->
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="apple-mobile-web-app-status-bar-style" content="default"/>
        <meta name="apple-mobile-web-app-title" content="OdooPWA"/>
        <link rel="apple-touch-icon" href="/web/static/img/icons/icon-152x152.png"/>

        <!-- Windows Support -->
        <meta name="msapplication-TileImage" content="/web/static/img/icons/icon-144x144.png"/>
        <meta name="msapplication-TileColor" content="#875A7B"/>
    </xpath>
</template>
```

## Service Worker Registration

### Registration Widget

```javascript
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ServiceWorkerRegistration = publicWidget.Widget.extend({
    selector: 'body',

    start: function() {
        if ('serviceWorker' in navigator) {
            this._registerServiceWorker();
            this._setupInstallPrompt();
        }
        return this._super(...arguments);
    },

    _registerServiceWorker: async function() {
        try {
            const registration = await navigator.serviceWorker.register('/service-worker.js', {
                scope: '/'
            });

            console.log('ServiceWorker registration successful:', registration.scope);

            // Check for updates
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        // New service worker available
                        this._showUpdateNotification();
                    }
                });
            });

        } catch (error) {
            console.error('ServiceWorker registration failed:', error);
        }
    },

    _setupInstallPrompt: function() {
        let deferredPrompt;

        window.addEventListener('beforeinstallprompt', (e) => {
            // Prevent the mini-infobar from appearing
            e.preventDefault();
            // Stash the event so it can be triggered later
            deferredPrompt = e;
            // Show install button
            this._showInstallButton(deferredPrompt);
        });

        window.addEventListener('appinstalled', () => {
            console.log('PWA was installed');
            this._hideInstallButton();
        });
    },

    _showInstallButton: function(deferredPrompt) {
        const installBtn = document.createElement('button');
        installBtn.className = 'btn btn-primary pwa-install-btn';
        installBtn.textContent = 'Install App';
        installBtn.style.position = 'fixed';
        installBtn.style.bottom = '20px';
        installBtn.style.right = '20px';
        installBtn.style.zIndex = '9999';

        installBtn.addEventListener('click', async () => {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            if (outcome === 'accepted') {
                this._hideInstallButton();
            }
        });

        document.body.appendChild(installBtn);
    },

    _hideInstallButton: function() {
        const btn = document.querySelector('.pwa-install-btn');
        if (btn) {
            btn.remove();
        }
    },

    _showUpdateNotification: function() {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info pwa-update-notification';
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            <p>A new version is available!</p>
            <button class="btn btn-sm btn-primary" onclick="location.reload()">Update</button>
        `;
        document.body.appendChild(notification);
    }
});

export default publicWidget.registry.ServiceWorkerRegistration;
```

## Push Notifications

### Client-Side Implementation

```javascript
/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

export class PushNotificationManager {
    constructor() {
        this.vapidPublicKey = 'YOUR_VAPID_PUBLIC_KEY';
    }

    async requestPermission() {
        const permission = await Notification.requestPermission();

        if (permission === 'granted') {
            console.log('Notification permission granted');
            await this.subscribeUser();
        } else {
            console.log('Notification permission denied');
        }
    }

    async subscribeUser() {
        try {
            const registration = await navigator.serviceWorker.ready;

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlB64ToUint8Array(this.vapidPublicKey)
            });

            console.log('User is subscribed:', subscription);

            // Send subscription to server
            await this.sendSubscriptionToServer(subscription);

        } catch (error) {
            console.error('Failed to subscribe user:', error);
        }
    }

    async sendSubscriptionToServer(subscription) {
        await rpc('/web/push/subscribe', {
            subscription: JSON.stringify(subscription)
        });
    }

    urlB64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    async unsubscribe() {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();

        if (subscription) {
            await subscription.unsubscribe();
            await rpc('/web/push/unsubscribe', {
                endpoint: subscription.endpoint
            });
        }
    }
}
```

### Service Worker Push Handler

```javascript
// In service-worker.js
self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'No payload',
        icon: '/web/static/img/icons/icon-192x192.png',
        badge: '/web/static/img/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'view',
                title: 'View',
                icon: '/web/static/img/icons/view.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/web/static/img/icons/close.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Odoo Notification', options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
```

## Background Sync

### Form Resilience with Background Sync

```javascript
// In service worker
self.addEventListener('sync', event => {
    if (event.tag === 'submit-form-data') {
        event.waitUntil(submitPendingForms());
    }
});

async function submitPendingForms() {
    const cache = await caches.open('form-submissions');
    const requests = await cache.keys();

    for (const request of requests) {
        try {
            const response = await fetch(request);
            if (response.ok) {
                await cache.delete(request);
                // Notify user of successful submission
                await self.registration.showNotification('Form Submitted', {
                    body: 'Your form was successfully submitted.',
                    icon: '/web/static/img/icons/success.png'
                });
            }
        } catch (error) {
            console.error('Sync failed, will retry:', error);
            // Will automatically retry later
        }
    }
}
```

### Client-Side Form Handler

```javascript
/** @odoo-module **/

export class ResilientFormHandler {
    constructor() {
        this.formSelector = 'form.resilient-form';
        this.init();
    }

    init() {
        document.querySelectorAll(this.formSelector).forEach(form => {
            form.addEventListener('submit', this.handleSubmit.bind(this));
        });
    }

    async handleSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);

        try {
            // Try to submit online
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.showSuccess('Form submitted successfully!');
                form.reset();
            }
        } catch (error) {
            // If offline, store for background sync
            await this.storeForSync(form.action, formData);
            this.showInfo('Form saved. Will submit when online.');
            await this.registerSync();
        }
    }

    async storeForSync(url, formData) {
        const cache = await caches.open('form-submissions');
        const request = new Request(url, {
            method: 'POST',
            body: formData
        });
        await cache.put(request, new Response());
    }

    async registerSync() {
        if ('sync' in self.registration) {
            await self.registration.sync.register('submit-form-data');
        }
    }

    showSuccess(message) {
        // Show success notification
    }

    showInfo(message) {
        // Show info notification
    }
}
```

## Offline Fallback Pages

### Create Offline Page

```html
<!-- static/src/offline.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - Odoo</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: #f8f9fa;
        }
        .offline-container {
            text-align: center;
            padding: 2rem;
        }
        .offline-icon {
            font-size: 4rem;
            color: #875A7B;
        }
        h1 {
            color: #212529;
            margin: 1rem 0;
        }
        p {
            color: #6c757d;
        }
        button {
            margin-top: 1rem;
            padding: 0.5rem 1.5rem;
            background: #875A7B;
            color: white;
            border: none;
            border-radius: 0.25rem;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="offline-container">
        <div class="offline-icon">📴</div>
        <h1>You're Offline</h1>
        <p>Please check your internet connection and try again.</p>
        <button onclick="location.reload()">Retry</button>
    </div>
</body>
</html>
```

## Performance Monitoring

```javascript
/** @odoo-module **/

export class PWAPerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }

    init() {
        // Monitor service worker registration time
        if ('serviceWorker' in navigator) {
            const startTime = performance.now();
            navigator.serviceWorker.ready.then(() => {
                this.metrics.swRegistrationTime = performance.now() - startTime;
                console.log(`Service Worker ready in ${this.metrics.swRegistrationTime}ms`);
            });
        }

        // Monitor cache performance
        this.monitorCachePerformance();

        // Monitor app install
        window.addEventListener('appinstalled', () => {
            this.metrics.appInstalled = true;
            this.sendMetrics();
        });
    }

    async monitorCachePerformance() {
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            const cacheStats = {};

            for (const name of cacheNames) {
                const cache = await caches.open(name);
                const requests = await cache.keys();
                cacheStats[name] = {
                    count: requests.length,
                    size: await this.estimateCacheSize(cache, requests)
                };
            }

            this.metrics.cacheStats = cacheStats;
        }
    }

    async estimateCacheSize(cache, requests) {
        let totalSize = 0;
        for (const request of requests) {
            const response = await cache.match(request);
            if (response && response.headers.get('content-length')) {
                totalSize += parseInt(response.headers.get('content-length'));
            }
        }
        return totalSize;
    }

    sendMetrics() {
        // Send metrics to analytics
        if (window.gtag) {
            gtag('event', 'pwa_performance', this.metrics);
        }
    }
}
```

## Testing PWA Features

```javascript
// tests/pwa.test.js
describe('PWA Features', () => {
    test('Service Worker registers successfully', async () => {
        const registration = await navigator.serviceWorker.register('/service-worker.js');
        expect(registration).toBeDefined();
        expect(registration.scope).toBe('http://localhost/');
    });

    test('Manifest is valid', async () => {
        const response = await fetch('/manifest.json');
        const manifest = await response.json();

        expect(manifest.name).toBeDefined();
        expect(manifest.icons.length).toBeGreaterThan(0);
        expect(manifest.start_url).toBeDefined();
    });

    test('Offline page loads', async () => {
        const response = await fetch('/offline.html');
        expect(response.status).toBe(200);
    });

    test('Push notifications permission', async () => {
        const permission = await Notification.requestPermission();
        expect(['granted', 'denied', 'default']).toContain(permission);
    });
});
```

## Odoo Controller for PWA

```python
# controllers/pwa.py
from odoo import http
from odoo.http import request
import json

class PWAController(http.Controller):

    @http.route('/manifest.json', type='http', auth='public', website=True)
    def manifest(self):
        website = request.website
        manifest = {
            "name": website.name,
            "short_name": website.name[:12],
            "description": website.social_default_description or "",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#875A7B",
            "theme_color": "#875A7B",
            "icons": self._get_icons(),
        }

        return request.make_response(
            json.dumps(manifest),
            headers=[('Content-Type', 'application/manifest+json')]
        )

    @http.route('/service-worker.js', type='http', auth='public')
    def service_worker(self):
        with open('path/to/service-worker.js', 'r') as f:
            content = f.read()

        return request.make_response(
            content,
            headers=[('Content-Type', 'application/javascript')]
        )

    @http.route('/web/push/subscribe', type='json', auth='user')
    def push_subscribe(self, subscription):
        # Store subscription in database
        user = request.env.user
        user.write({'push_subscription': subscription})
        return {'status': 'success'}

    @http.route('/web/push/unsubscribe', type='json', auth='user')
    def push_unsubscribe(self, endpoint):
        # Remove subscription
        user = request.env.user
        user.write({'push_subscription': False})
        return {'status': 'success'}

    def _get_icons(self):
        return [
            {"src": "/web/static/img/icons/icon-192x192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/web/static/img/icons/icon-512x512.png", "sizes": "512x512", "type": "image/png"},
        ]
```

## Best Practices

1. **Cache Strategy**
   - Use Network First for API calls
   - Cache First for static assets
   - Stale While Revalidate for HTML pages

2. **Service Worker Updates**
   - Implement skipWaiting for immediate updates
   - Show update notifications to users
   - Version your cache names

3. **Performance**
   - Limit cache size to avoid storage issues
   - Implement cache expiration
   - Use lazy loading for non-critical resources

4. **Offline Experience**
   - Provide meaningful offline pages
   - Cache critical resources during install
   - Implement background sync for forms

5. **Push Notifications**
   - Request permission at the right time
   - Provide clear opt-out options
   - Send relevant, timely notifications

6. **Testing**
   - Test offline scenarios
   - Verify manifest validity
   - Check Lighthouse PWA score
   - Test on various devices and networks