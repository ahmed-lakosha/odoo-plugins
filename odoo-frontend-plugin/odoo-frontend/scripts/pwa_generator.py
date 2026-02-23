#!/usr/bin/env python3
"""
PWA Generator for Odoo Websites
Generates Service Worker, Web App Manifest, and registration code
"""

import json
import os
import argparse
from pathlib import Path


class PWAGenerator:
    def __init__(self, module_path, module_name):
        self.module_path = Path(module_path)
        self.module_name = module_name
        self.static_path = self.module_path / 'static'
        self.src_path = self.static_path / 'src'

    def generate_service_worker(self):
        """Generate service-worker.js with caching strategies"""
        sw_content = '''// Service Worker for {module_name}
const CACHE_NAME = '{module_name}-pwa-v1';
const urlsToCache = [
  '/',
  '/web/static/lib/owl/owl.js',
  '/web/static/src/legacy/js/public/public_root.js',
  '/web/static/src/libs/fontawesome/css/font-awesome.css'
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
  self.skipWaiting();
});

// Fetch event with caching strategies
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);

  // Network first for API calls
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/web/dataset/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Cache first for static assets
  if (request.destination === 'image' ||
      request.destination === 'style' ||
      request.destination === 'script' ||
      url.pathname.includes('/web/static/')) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Stale while revalidate for HTML
  if (request.mode === 'navigate') {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Default to network
  event.respondWith(fetch(request));
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
  self.clients.claim();
});

// Push notification handling
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'New notification',
    icon: '/web/static/img/icons/icon-192x192.png',
    badge: '/web/static/img/icons/badge-72x72.png',
    vibrate: [100, 50, 100]
  };

  event.waitUntil(
    self.registration.showNotification('Odoo Notification', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});

// Background sync
self.addEventListener('sync', event => {
  if (event.tag === 'submit-form-data') {
    event.waitUntil(submitPendingForms());
  }
});

// Caching strategies
function networkFirst(request) {
  return fetch(request)
    .then(response => {
      const responseClone = response.clone();
      caches.open(CACHE_NAME).then(cache => {
        cache.put(request, responseClone);
      });
      return response;
    })
    .catch(() => caches.match(request));
}

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

async function submitPendingForms() {
  const cache = await caches.open('form-submissions');
  const requests = await cache.keys();

  for (const request of requests) {
    try {
      const response = await fetch(request);
      if (response.ok) {
        await cache.delete(request);
        await self.registration.showNotification('Form Submitted', {
          body: 'Your offline form was successfully submitted.',
          icon: '/web/static/img/icons/success.png'
        });
      }
    } catch (error) {
      console.error('Sync failed, will retry:', error);
    }
  }
}
'''.format(module_name=self.module_name)

        sw_path = self.src_path / 'service-worker.js'
        sw_path.parent.mkdir(parents=True, exist_ok=True)
        sw_path.write_text(sw_content)
        print(f"✅ Created service worker: {sw_path}")

    def generate_manifest(self, app_name=None, theme_color='#875A7B'):
        """Generate Web App Manifest"""
        if not app_name:
            app_name = self.module_name.replace('_', ' ').title()

        manifest = {
            "name": f"{app_name} - Odoo PWA",
            "short_name": app_name[:12],
            "description": f"{app_name} Progressive Web Application",
            "start_url": "/?utm_source=pwa",
            "scope": "/",
            "display": "standalone",
            "orientation": "portrait-primary",
            "background_color": theme_color,
            "theme_color": theme_color,
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
                    "type": "image/png",
                    "platform": "wide"
                },
                {
                    "src": "/web/static/img/screenshots/mobile.png",
                    "sizes": "750x1334",
                    "type": "image/png",
                    "platform": "narrow"
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
            "prefer_related_applications": False
        }

        manifest_path = self.src_path / 'manifest.json'
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print(f"✅ Created manifest: {manifest_path}")

    def generate_registration_widget(self):
        """Generate public widget for service worker registration"""
        widget_content = '''/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.ServiceWorkerRegistration = publicWidget.Widget.extend({
    selector: 'body',

    start: function() {
        if ('serviceWorker' in navigator) {
            this._registerServiceWorker();
            this._setupInstallPrompt();
            this._checkNotificationPermission();
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
            e.preventDefault();
            deferredPrompt = e;
            this._showInstallButton(deferredPrompt);
        });

        window.addEventListener('appinstalled', () => {
            console.log('PWA was installed');
            this._hideInstallButton();
            this._trackInstallation();
        });
    },

    _checkNotificationPermission: function() {
        if ('Notification' in window && Notification.permission === 'default') {
            // Show notification permission prompt at appropriate time
            setTimeout(() => {
                this._requestNotificationPermission();
            }, 30000); // After 30 seconds
        }
    },

    async _requestNotificationPermission() {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            console.log('Notification permission granted');
            // Subscribe to push notifications if needed
            await this._subscribeToPush();
        }
    },

    async _subscribeToPush() {
        try {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this._urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
            });

            // Send subscription to server
            await this.rpc('/web/push/subscribe', {
                subscription: JSON.stringify(subscription)
            });
        } catch (error) {
            console.error('Failed to subscribe to push notifications:', error);
        }
    },

    _showInstallButton: function(deferredPrompt) {
        const installBtn = $('<button/>', {
            'class': 'btn btn-primary pwa-install-btn',
            'text': 'Install App',
            'css': {
                'position': 'fixed',
                'bottom': '20px',
                'right': '20px',
                'z-index': '9999',
                'display': 'none'
            }
        });

        installBtn.on('click', async () => {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to install prompt: ${outcome}`);
            if (outcome === 'accepted') {
                this._hideInstallButton();
            }
        });

        $('body').append(installBtn);
        installBtn.fadeIn();
    },

    _hideInstallButton: function() {
        $('.pwa-install-btn').fadeOut().remove();
    },

    _showUpdateNotification: function() {
        const notification = $('<div/>', {
            'class': 'alert alert-info pwa-update-notification',
            'css': {
                'position': 'fixed',
                'top': '20px',
                'right': '20px',
                'z-index': '9999'
            },
            'html': '<p>A new version is available!</p><button class="btn btn-sm btn-primary" onclick="location.reload()">Update</button>'
        });

        $('body').append(notification);
        setTimeout(() => notification.fadeOut().remove(), 10000);
    },

    _trackInstallation: function() {
        // Track PWA installation
        if (window.gtag) {
            gtag('event', 'pwa_installed', {
                'event_category': 'engagement',
                'event_label': 'PWA Installation'
            });
        }
    },

    _urlBase64ToUint8Array: function(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/\\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
});

export default publicWidget.registry.ServiceWorkerRegistration;
'''

        widget_path = self.src_path / 'js' / 'pwa_registration.js'
        widget_path.parent.mkdir(parents=True, exist_ok=True)
        widget_path.write_text(widget_content)
        print(f"✅ Created registration widget: {widget_path}")

    def generate_offline_page(self):
        """Generate offline fallback page"""
        offline_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Offline - {module_name}</title>
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
            margin-bottom: 1rem;
        }
        h1 {
            color: #212529;
            margin: 1rem 0;
            font-size: 2rem;
        }
        p {
            color: #6c757d;
            margin-bottom: 2rem;
        }
        button {
            padding: 0.75rem 2rem;
            background: #875A7B;
            color: white;
            border: none;
            border-radius: 0.25rem;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #714968;
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
'''.format(module_name=self.module_name)

        offline_path = self.static_path / 'offline.html'
        offline_path.parent.mkdir(parents=True, exist_ok=True)
        offline_path.write_text(offline_content)
        print(f"✅ Created offline page: {offline_path}")

    def generate_all(self, app_name=None, theme_color='#875A7B'):
        """Generate all PWA files"""
        print(f"\n🚀 Generating PWA files for {self.module_name}...\n")

        self.generate_service_worker()
        self.generate_manifest(app_name, theme_color)
        self.generate_registration_widget()
        self.generate_offline_page()

        print(f"\n✨ PWA generation complete!")
        print(f"\n📝 Next steps:")
        print(f"1. Add the registration widget to your manifest assets:")
        print(f"   'web.assets_frontend': ['static/src/js/pwa_registration.js']")
        print(f"2. Link manifest in your base template")
        print(f"3. Create icon files in static/img/icons/")
        print(f"4. Test service worker registration")
        print(f"5. Run Lighthouse PWA audit")


def main():
    parser = argparse.ArgumentParser(description='Generate PWA files for Odoo module')
    parser.add_argument('module_path', help='Path to Odoo module')
    parser.add_argument('--name', help='App name for manifest')
    parser.add_argument('--color', default='#875A7B', help='Theme color (default: #875A7B)')

    args = parser.parse_args()

    # Extract module name from path
    module_path = Path(args.module_path)
    module_name = module_path.name

    generator = PWAGenerator(module_path, module_name)
    generator.generate_all(args.name, args.color)


if __name__ == '__main__':
    main()