"""
Script to add PWA routes to the main Flask application.
This allows Progressive Web App functionality to be integrated directly into the Flask app.

Usage:
python fix_pwa_routes.py --app-dir=/path/to/your/app
"""

import os
import argparse
import shutil
from pathlib import Path


def ensure_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def create_pwa_routes_file(app_dir):
    """Create routes_pwa.py file with PWA routes"""
    routes_file = os.path.join(app_dir, 'routes_pwa.py')
    
    # Don't overwrite if file already exists
    if os.path.exists(routes_file):
        print(f"PWA routes file already exists at {routes_file}")
        return
    
    with open(routes_file, 'w') as f:
        f.write('''"""
Routes for Progressive Web App (PWA) functionality
"""
from flask import send_from_directory, current_app
from main import app

# Serve the service worker from the root directory
@app.route('/service-worker.js')
def service_worker():
    """Serve the service worker file from the static folder"""
    return send_from_directory('static/js', 'service-worker.js')

# Serve the manifest file
@app.route('/manifest.json')
def manifest():
    """Serve the manifest file from the static folder"""
    return send_from_directory('static', 'manifest.json')

# Serve the offline page
@app.route('/offline')
def offline():
    """Display the offline fallback page"""
    return current_app.send_static_file('offline.html')
''')
    print(f"Created PWA routes file at {routes_file}")


def create_service_worker(app_dir):
    """Create service worker JS file"""
    js_dir = os.path.join(app_dir, 'static/js')
    ensure_directory(js_dir)
    
    service_worker_file = os.path.join(js_dir, 'service-worker.js')
    
    # Don't overwrite if file already exists
    if os.path.exists(service_worker_file):
        print(f"Service worker file already exists at {service_worker_file}")
        return
    
    with open(service_worker_file, 'w') as f:
        f.write('''// HealthyRizz Service Worker

const CACHE_NAME = 'healthyrizz-cache-v1';
const URLS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/static/manifest.json'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(URLS_TO_CACHE);
      })
  );
});

// Activate event - clean up old caches
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
});

// Fetch event - respond with cached resources when offline
self.addEventListener('fetch', event => {
  // Skip non-GET requests and requests to external resources
  if (event.request.method !== 'GET' || !event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // For HTML pages - network first, then cache
  if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Clone the response before using it
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
          return response;
        })
        .catch(() => {
          return caches.match(event.request)
            .then(response => {
              return response || caches.match('/offline');
            });
        })
    );
    return;
  }

  // For other resources - cache first, then network
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached response if available
        if (response) {
          return response;
        }

        // Otherwise fetch from network
        return fetch(event.request)
          .then(response => {
            // Clone the response before using it
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            return response;
          })
          .catch(error => {
            console.log('Fetch failed:', error);
          });
      })
  );
});
''')
    print(f"Created service worker file at {service_worker_file}")


def create_register_sw(app_dir):
    """Create service worker registration JS file"""
    js_dir = os.path.join(app_dir, 'static/js')
    ensure_directory(js_dir)
    
    register_sw_file = os.path.join(js_dir, 'register-sw.js')
    
    # Don't overwrite if file already exists
    if os.path.exists(register_sw_file):
        print(f"Service worker registration file already exists at {register_sw_file}")
        return
    
    with open(register_sw_file, 'w') as f:
        f.write('''// Register service worker for PWA functionality
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      })
      .catch(error => {
        console.log('ServiceWorker registration failed: ', error);
      });
  });
}
''')
    print(f"Created service worker registration file at {register_sw_file}")


def create_manifest(app_dir):
    """Create manifest.json file"""
    static_dir = os.path.join(app_dir, 'static')
    ensure_directory(static_dir)
    
    manifest_file = os.path.join(static_dir, 'manifest.json')
    
    # Don't overwrite if file already exists
    if os.path.exists(manifest_file):
        print(f"Manifest file already exists at {manifest_file}")
        return
    
    with open(manifest_file, 'w') as f:
        f.write('''{
  "name": "HealthyRizz Meal Delivery",
  "short_name": "HealthyRizz",
  "description": "Healthy meal delivery service for fitness-focused individuals",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#4CAF50",
  "icons": [
    {
      "src": "/static/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
''')
    print(f"Created manifest file at {manifest_file}")


def create_offline_page(app_dir):
    """Create offline.html page"""
    static_dir = os.path.join(app_dir, 'static')
    ensure_directory(static_dir)
    
    offline_file = os.path.join(static_dir, 'offline.html')
    
    # Don't overwrite if file already exists
    if os.path.exists(offline_file):
        print(f"Offline page already exists at {offline_file}")
        return
    
    with open(offline_file, 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthyRizz - Offline</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
            text-align: center;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4CAF50;
        }
        .icon {
            font-size: 60px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📶</div>
        <h1>You're Offline</h1>
        <p>Sorry, you need an internet connection to access HealthyRizz.</p>
        <p>Please check your connection and try again.</p>
        <p>Some features of HealthyRizz are available offline, but you'll need to connect to browse meals and place orders.</p>
    </div>
</body>
</html>
''')
    print(f"Created offline page at {offline_file}")


def create_placeholder_icons(app_dir):
    """Create placeholder icons in various sizes"""
    icons_dir = os.path.join(app_dir, 'static/icons')
    ensure_directory(icons_dir)
    
    # Check if Python PIL/Pillow is available
    try:
        from PIL import Image, ImageDraw
        
        # Create icons in different sizes
        sizes = [192, 512]
        for size in sizes:
            icon_file = os.path.join(icons_dir, f'icon-{size}x{size}.png')
            
            # Don't overwrite if file already exists
            if os.path.exists(icon_file):
                print(f"Icon already exists at {icon_file}")
                continue
                
            # Create a simple colored square icon
            img = Image.new('RGB', (size, size), color=(76, 175, 80))
            draw = ImageDraw.Draw(img)
            draw.text((size//4, size//3), "HealthyRizz", fill=(255, 255, 255))
            
            img.save(icon_file)
            print(f"Created icon at {icon_file}")
            
    except ImportError:
        print("Warning: PIL/Pillow is not available. Icons will not be created.")
        print("Please create icons manually or install Pillow with: pip install Pillow")


def update_main_py(app_dir):
    """Update main.py to import PWA routes"""
    main_py_file = os.path.join(app_dir, 'main.py')
    
    if not os.path.exists(main_py_file):
        print(f"Error: main.py file not found at {main_py_file}")
        return
    
    with open(main_py_file, 'r') as f:
        content = f.read()
    
    # Check if PWA routes are already imported
    if 'import routes_pwa' in content:
        print("PWA routes already imported in main.py")
        return
    
    # Add import at the end of the file (before if __name__ == '__main__')
    if 'if __name__' in content:
        # Insert before if __name__ block
        main_py_content = content.replace(
            'if __name__', 
            '\n# Import PWA routes\ntry:\n    import routes_pwa\n    print("✅ PWA routes imported successfully")\nexcept Exception as e:\n    print(f"❌ Error importing PWA routes: {str(e)}")\n\nif __name__'
        )
    else:
        # Append to the end of the file
        main_py_content = content + '\n\n# Import PWA routes\ntry:\n    import routes_pwa\n    print("✅ PWA routes imported successfully")\nexcept Exception as e:\n    print(f"❌ Error importing PWA routes: {str(e)}")\n'
    
    with open(main_py_file, 'w') as f:
        f.write(main_py_content)
    
    print("Updated main.py to import PWA routes")


def update_base_template(app_dir):
    """Update base template with PWA meta tags"""
    templates_dir = os.path.join(app_dir, 'templates')
    ensure_directory(templates_dir)
    
    base_template = os.path.join(templates_dir, 'base.html')
    
    if not os.path.exists(base_template):
        print(f"Warning: base.html not found at {base_template}. Skipping template update.")
        return
    
    with open(base_template, 'r') as f:
        content = f.read()
    
    # Check if PWA meta tags are already added
    if 'manifest.json' in content and 'apple-mobile-web-app-capable' in content:
        print("PWA meta tags already present in base.html")
        return
    
    # Add PWA meta tags before closing head tag
    head_close_tag = '</head>'
    pwa_meta_tags = '''
    <!-- PWA Support -->
    <link rel="manifest" href="{{ url_for('static', filename='manifest.json') }}">
    <meta name="theme-color" content="#4CAF50">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="HealthyRizz">
    
    <!-- iOS icons -->
    <link rel="apple-touch-icon" href="{{ url_for('static', filename='icons/icon-192x192.png') }}">
    <link rel="apple-touch-icon" sizes="152x152" href="{{ url_for('static', filename='icons/icon-192x192.png') }}">
    <link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='icons/icon-192x192.png') }}">
    <link rel="apple-touch-icon" sizes="167x167" href="{{ url_for('static', filename='icons/icon-192x192.png') }}">
    
    <!-- Service Worker Registration -->
    <script src="{{ url_for('static', filename='js/register-sw.js') }}" defer></script>
    '''
    
    # Insert PWA meta tags before </head>
    updated_content = content.replace(head_close_tag, f"{pwa_meta_tags}\n{head_close_tag}")
    
    with open(base_template, 'w') as f:
        f.write(updated_content)
    
    print("Updated base.html with PWA meta tags")


def main():
    parser = argparse.ArgumentParser(description='Add PWA functionality to HealthyRizz Flask app')
    parser.add_argument('--app-dir', type=str, default='.', help='Application directory path')
    args = parser.parse_args()
    
    app_dir = args.app_dir
    
    # Make sure the app directory exists
    if not os.path.isdir(app_dir):
        print(f"Error: Directory {app_dir} does not exist")
        return
    
    print(f"Adding PWA functionality to app in {app_dir}")
    
    # Create all necessary PWA files
    create_pwa_routes_file(app_dir)
    create_service_worker(app_dir)
    create_register_sw(app_dir)
    create_manifest(app_dir)
    create_offline_page(app_dir)
    create_placeholder_icons(app_dir)
    
    # Update existing files
    update_main_py(app_dir)
    update_base_template(app_dir)
    
    print("\nPWA functionality has been successfully added!")
    print("Restart your Flask application for the changes to take effect.")
    print("If you're using a gunicorn service, run: sudo systemctl restart healthyrizz")


if __name__ == '__main__':
    main()