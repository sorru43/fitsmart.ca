# FitSmart Project Structure

## 🏗️ Core Application Files

### Main Application
- `app.py` - Main Flask application entry point
- `main.py` - Alternative entry point for systemd service
- `config.py` - Application configuration
- `config_production.py` - Production-specific configuration

### Database
- `database/` - Database models and configuration
  - `models.py` - SQLAlchemy models
  - `db_config.py` - Database configuration
  - `init_db.py` - Database initialization

### Routes
- `routes/` - Flask route blueprints
  - `main_routes.py` - Main website routes
  - `admin_routes.py` - Admin panel routes
  - `admin_orders.py` - Order management routes
  - `subscription_management_routes.py` - Subscription routes

### Forms
- `forms/` - WTForms form definitions
  - `auth_forms.py` - Authentication forms
  - `checkout_forms.py` - Checkout forms

### Templates
- `templates/` - Jinja2 HTML templates
  - `base.html` - Base template with bundled CSS
  - `index.html` - Homepage
  - `admin/` - Admin panel templates
  - `profile/` - User profile templates

### Static Files
- `static/` - Static assets
  - `css/main.min.css` - **Bundled and minified CSS** (2.9MB)
  - `js/` - JavaScript files
  - `images/` - Images and icons
  - `fonts/` - Font files
  - `uploads/` - User uploads

## 🛠️ Build & Deployment Tools

### CSS Bundling (Python-based)
- `build_css.py` - Bundles all CSS into main.min.css
- `deploy_css.py` - Deploys CSS changes to VPS

### Service Management
- `fitsmart.service` - Systemd service configuration
- `gunicorn.conf.py` - Gunicorn configuration

## 📁 Key Directories

### Core Directories
- `migrations/` - Database migrations
- `utils/` - Utility functions and helpers
- `scripts/` - Utility scripts
- `docs/` - Documentation

### Configuration
- `instance/` - Instance-specific files
- `venv/` - Python virtual environment

## 🚀 Deployment Files

### Production Configuration
- `nginx.conf` - Nginx configuration
- `fitsmart.conf` - Application-specific nginx config

### Deployment Scripts
- `deployment_scripts/` - Various deployment scripts
- `deploy_fitsmart_in_cloudpanel.sh` - CloudPanel deployment

## 🧹 Clean Project Benefits

✅ **Single CSS file** - No more PageSpeed/service worker conflicts  
✅ **Python-based build** - No Node.js dependencies  
✅ **Clean structure** - Easy to navigate and maintain  
✅ **Production-ready** - Optimized for VPS deployment  
✅ **Fast loading** - Minified and bundled assets  

## 🔄 Workflow

### Development
1. Edit CSS files in `static/css/`
2. Run `python build_css.py` to bundle
3. Test locally

### Deployment
1. Upload changes to VPS
2. Run `python3 deploy_css.py` on VPS
3. Website automatically uses new CSS

## 📊 File Sizes

- **main.min.css**: 2.9MB (all styles bundled)
- **Total project**: ~50MB (clean and optimized)
- **No duplicate files** - All unused files removed

This is now a **clean, production-ready Flask application** with optimized CSS bundling and no unnecessary files! 