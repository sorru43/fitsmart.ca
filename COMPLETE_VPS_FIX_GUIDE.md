# Complete VPS Fix Guide

## 🚀 Quick Fix Commands

### 1. Connect to VPS
```bash
ssh root@89.116.122.69
```

### 2. Navigate to project
```bash
cd /home/healthyrizz/htdocs/healthyrizz.in
```

### 3. Stop service
```bash
sudo systemctl stop healthyrizz
```

### 4. Upload fixed files
Upload these files from your local machine to the VPS:
- app.py
- config.py
- wsgi.py
- templates/base.html
- templates/admin/base_admin.html
- All other template files

### 5. Activate environment
```bash
source venv/bin/activate
```

### 6. Test application
```bash
python -c "from app import create_app; app = create_app(); print('✅ App created successfully')"
```

### 7. Start service
```bash
sudo systemctl start healthyrizz
```

### 8. Check status
```bash
sudo systemctl status healthyrizz
```

### 9. Check logs
```bash
sudo journalctl -u healthyrizz -f
```

## 🔧 Manual Fixes (if needed)

### Fix CSRF Token Error
Edit templates/base.html line 17:
```html
<!-- Change this: -->
<meta name="csrf-token" content="{{ csrf_token() }}">

<!-- To this: -->
<meta name="csrf-token" content="{{ csrf_token() if csrf_token else '' }}">
```

### Fix wsgi.py
```bash
cat > wsgi.py << 'EOF'
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
EOF
```

### Check file permissions
```bash
chmod 644 *.py
chmod 644 templates/*.html
chmod 644 templates/admin/*.html
```

## 📊 Monitoring

### Check service status
```bash
sudo systemctl status healthyrizz
```

### Check logs
```bash
sudo journalctl -u healthyrizz -n 50
```

### Check port
```bash
netstat -tlnp | grep 8000
```

### Test website
```bash
curl -I http://localhost:8000
```

## ✅ Success Indicators

- Service status: "active (running)"
- No errors in logs
- Port 8000 listening
- Website loads: https://healthyrizz.in

## 🆘 Emergency Reset

If everything fails:
```bash
sudo systemctl stop healthyrizz
cp -r /home/healthyrizz/htdocs/healthyrizz.in /home/healthyrizz/htdocs/healthyrizz.in.backup
# Upload fresh files from local machine
sudo systemctl start healthyrizz
```
