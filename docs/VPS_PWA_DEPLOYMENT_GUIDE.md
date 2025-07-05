# Adding PWA Functionality to HealthyRizz on VPS

This guide explains how to add Progressive Web App (PWA) functionality to your running HealthyRizz application on a VPS.

## Method 1: Using the Deployment Script

1. **Edit the deployment script with your VPS details**:
   Open `deploy_pwa_to_vps.sh` and update:
   ```bash
   VPS_USER="root"  # or your user
   VPS_HOST="your.vps.ip.address"  # your actual VPS IP or hostname
   APP_DIR="/home/healthyrizz/htdocs/www.healthyrizz.ca"  # confirm this path
   ```

2. **Make the script executable**:
   ```bash
   chmod +x deploy_pwa_to_vps.sh
   ```

3. **Run the script**:
   ```bash
   ./deploy_pwa_to_vps.sh
   ```

4. **Restart the HealthyRizz service**:
   ```bash
   sudo systemctl restart healthyrizz
   ```

## Method 2: Manual Deployment

If you prefer to deploy the PWA functionality manually:

1. **SSH into your VPS**:
   ```bash
   ssh root@your.vps.ip.address
   ```

2. **Navigate to the HealthyRizz directory**:
   ```bash
   cd /home/healthyrizz/htdocs/www.healthyrizz.ca
   ```

3. **Create necessary directories**:
   ```bash
   mkdir -p static/js static/icons
   ```

4. **Create the PWA files one by one using a text editor like nano**:

   **a. Create manifest.json**:
   ```bash
   nano static/manifest.json
   ```
   Paste the content of the manifest.json file and save.

   **b. Create service-worker.js**:
   ```bash
   nano static/js/service-worker.js
   ```
   Paste the content of the service-worker.js file and save.

   **c. Create register-sw.js**:
   ```bash
   nano static/js/register-sw.js
   ```
   Paste the content of the register-sw.js file and save.

   **d. Create offline.html**:
   ```bash
   nano static/offline.html
   ```
   Paste the content of the offline.html file and save.

5. **Generate PWA icons**:
   - For simplicity, you can use an online tool to create your icons
   - Save them to `/static/icons/` with names like `icon-192x192.png`, `icon-512x512.png`, etc.

6. **Create routes_pwa.py**:
   ```bash
   nano routes_pwa.py
   ```
   Paste the following content:
   ```python
   """
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
   ```

7. **Update main.py to import PWA routes**:
   ```bash
   nano main.py
   ```
   At the end of the file (but before `if __name__ == '__main__'`), add:
   ```python
   # Import PWA routes
   try:
       import routes_pwa
       print("✅ PWA routes imported successfully")
   except Exception as e:
       print(f"❌ Error importing PWA routes: {str(e)}")
   ```

8. **Update base.html with PWA meta tags**:
   ```bash
   nano templates/base.html
   ```
   Before the closing `</head>` tag, add:
   ```html
   <!-- PWA Support -->
   <link rel="manifest" href="{{ url_for('static', filename='manifest.json') }}">
   <meta name="theme-color" content="#4CAF50">
   <meta name="apple-mobile-web-app-capable" content="yes">
   <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
   <meta name="apple-mobile-web-app-title" content="HealthyRizz">
   
   <!-- iOS icons -->
   <link rel="apple-touch-icon" href="{{ url_for('static', filename='icons/icon-192x192.png') }}">
   <link rel="apple-touch-icon" sizes="152x152" href="{{ url_for('static', filename='icons/icon-152x152.png') }}">
   <link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='icons/icon-192x192.png') }}">
   <link rel="apple-touch-icon" sizes="167x167" href="{{ url_for('static', filename='icons/icon-152x152.png') }}">
   
   <!-- Service Worker Registration -->
   <script src="{{ url_for('static', filename='js/register-sw.js') }}" defer></script>
   ```

9. **Restart the HealthyRizz service**:
   ```bash
   sudo systemctl restart healthyrizz
   ```

## Testing PWA Functionality

After deployment:

1. Visit your website in Chrome or Edge
2. Open Developer Tools (F12)
3. Go to the "Application" tab
4. Look for "Manifest" and "Service Workers" in the sidebar
5. Verify these sections show your PWA configuration
6. Check if you see an "Install" button in your browser's address bar or menu

## Troubleshooting

If PWA functionality doesn't work:

1. **Check browser logs** for errors
2. **Verify service worker registration** in the browser's Application tab
3. **Check file paths** - ensure all URLs in the manifest are correct
4. **Verify HTTPS** - PWAs require a secure context (HTTPS)
5. **Clear cache** - sometimes you need to clear the browser cache to see changes
6. **Restart the application** if changes aren't visible

For any issues, check the application logs:
```bash
sudo journalctl -u healthyrizz -n 100
```
