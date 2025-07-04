# Setting Up HealthyRizz PWA with Push Notifications on CloudPanel

This guide shows how to set up the HealthyRizz Progressive Web App (PWA) with push notifications on a CloudPanel VPS.

## Prerequisites

- CloudPanel installed on your VPS
- Domain configured in CloudPanel
- PostgreSQL database set up

## One-Shot Deployment (Recommended)

For a complete setup that handles everything automatically:

1. Upload `deploy_healthyrizz_cloudpanel.sh` to your server
2. Make it executable:
   ```bash
   chmod +x deploy_healthyrizz_cloudpanel.sh
   ```
3. Run the script:
   ```bash
   sudo ./deploy_healthyrizz_cloudpanel.sh
   ```

This script will:
- Set up the Python virtual environment
- Install all required dependencies
- Create the database schema
- Configure PWA and push notification functionality
- Set up the systemd service

## Manual Setup Steps

If you prefer to manually set up each component:

### 1. Prepare the Environment

1. Install required packages on your server:
   ```bash
   apt update
   apt install python3-pip python3-venv nginx
   ```

2. Create a directory for the application:
   ```bash
   mkdir -p /home/healthyrizz/htdocs/www.healthyrizz.ca
   cd /home/healthyrizz/htdocs/www.healthyrizz.ca
   ```

3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-wtf pywebpush py-vapid gunicorn psycopg2-binary python-dotenv
   ```

### 2. Set Up PWA Files

1. Create the static directory structure:
   ```bash
   mkdir -p static/js static/icons static/css templates
   ```

2. Create the PWA manifest file:
   ```bash
   cat > static/manifest.json << EOF
   {
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
   EOF
   ```

3. Create the service worker file:
   ```bash
   cat > static/js/service-worker.js << EOF
   // HealthyRizz Service Worker with push notifications support
   
   const CACHE_NAME = 'healthyrizz-cache-v1';
   const URLS_TO_CACHE = [
     '/',
     '/static/css/style.css',
     '/static/js/main.js',
     '/static/icons/icon-192x192.png',
     '/static/icons/icon-512x512.png',
     '/static/manifest.json',
     '/offline'
   ];
   
   // Installation - cache essential files
   self.addEventListener('install', event => {
     event.waitUntil(
       caches.open(CACHE_NAME)
         .then(cache => {
           console.log('Opened cache');
           return cache.addAll(URLS_TO_CACHE);
         })
     );
   });
   
   // Activation - clean up old caches
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
   
   // Fetch handler - respond with cached resources when offline
   self.addEventListener('fetch', event => {
     // Handle fetch requests...
   });
   
   // Push notification handler
   self.addEventListener('push', event => {
     console.log('Push received:', event);
     
     let notificationData = {};
     
     if (event.data) {
       try {
         notificationData = event.data.json();
       } catch (e) {
         notificationData = {
           title: 'HealthyRizz Notification',
           message: event.data.text()
         };
       }
     }
     
     const title = notificationData.title || 'HealthyRizz Notification';
     const options = {
       body: notificationData.message || 'You have a new notification!',
       icon: '/static/icons/icon-192x192.png',
       badge: '/static/icons/icon-192x192.png',
       data: {
         url: notificationData.url || '/'
       }
     };
     
     event.waitUntil(
       self.registration.showNotification(title, options)
     );
   });
   
   // Notification click handler
   self.addEventListener('notificationclick', event => {
     event.notification.close();
     
     // Open URL when notification is clicked
     const urlToOpen = event.notification.data && event.notification.data.url
       ? new URL(event.notification.data.url, self.location.origin).href
       : self.location.origin;
       
     event.waitUntil(
       clients.openWindow(urlToOpen)
     );
   });
   EOF
   ```

### 3. Set Up Flask Application with Push Notifications

1. Create the main application file:
   ```bash
   cat > main.py << EOF
   # Main application file with PWA and push notification support
   # ... (Flask application code) ...
   
   # Import PWA routes
   try:
       import routes_pwa
       app.logger.info("✅ PWA routes imported successfully")
   except Exception as e:
       app.logger.error(f"❌ Error importing PWA routes: {str(e)}")
   
   # Import notification routes
   try:
       import routes_notifications
       app.logger.info("✅ Notification routes imported successfully")
   except Exception as e:
       app.logger.error(f"❌ Error importing notification routes: {str(e)}")
   EOF
   ```

2. Create the notification routes file:
   ```bash
   cat > routes_notifications.py << EOF
   # Routes for push notification functionality
   # ... (Notification routes code) ...
   EOF
   ```

3. Create the PWA routes file:
   ```bash
   cat > routes_pwa.py << EOF
   # Routes for PWA functionality
   # ... (PWA routes code) ...
   EOF
   ```

### 4. Generate VAPID Keys

1. Create the VAPID key generation script:
   ```bash
   cat > generate_vapid_keys.py << EOF
   # Script to generate VAPID keys for push notifications
   # ... (VAPID key generation code) ...
   EOF
   ```

2. Run the script to generate keys:
   ```bash
   python generate_vapid_keys.py --email admin@healthyrizz.ca
   ```

### 5. Set Up Systemd Service

1. Create a systemd service file:
   ```bash
   cat > /etc/systemd/system/healthyrizz.service << EOF
   [Unit]
   Description=HealthyRizz Meal Delivery Service
   After=network.target
   
   [Service]
   User=healthyrizz
   Group=www-data
   WorkingDirectory=/home/healthyrizz/htdocs/www.healthyrizz.ca
   Environment="PATH=/home/healthyrizz/htdocs/www.healthyrizz.ca/venv/bin"
   ExecStart=/home/healthyrizz/htdocs/www.healthyrizz.ca/venv/bin/gunicorn main:app -b 127.0.0.1:8090 --workers 3
   Restart=always
   RestartSec=5
   
   [Install]
   WantedBy=multi-user.target
   EOF
   ```

2. Enable and start the service:
   ```bash
   systemctl daemon-reload
   systemctl enable healthyrizz
   systemctl start healthyrizz
   ```

### 6. Configure Nginx with CloudPanel

In CloudPanel:

1. Go to Sites > your-domain > Settings > Nginx
2. Add custom Nginx directives:
   ```nginx
   # Proxy requests to the Gunicorn server
   location / {
       proxy_pass http://127.0.0.1:8090;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   
   # Serve static files directly
   location /static {
       alias /home/healthyrizz/htdocs/www.healthyrizz.ca/static;
       expires 30d;
   }
   ```

3. Apply changes and restart Nginx.

## Verify Installation

1. Visit your website with HTTPS
2. Check the browser console for the service worker registration
3. Test notification permission prompts
4. Send a test notification from the `/notification-test` page

## Troubleshooting

If you encounter issues:

1. Check service logs:
   ```bash
   journalctl -u healthyrizz -n 50
   ```

2. Check Nginx logs:
   ```bash
   tail -n 50 /var/log/nginx/error.log
   ```

3. Verify VAPID keys are correctly generated in `.env`

4. Ensure the service worker is registered in the browser's Application tab
