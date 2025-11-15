# VPS Fix Commands

## 🔧 **Fix VPS Deployment Issues**

### **Step 1: Connect to your VPS**
```bash
ssh root@89.116.122.69
```

### **Step 2: Navigate to your project directory**
```bash
cd /home/healthyrizz/htdocs/healthyrizz.in
```

### **Step 3: Activate virtual environment**
```bash
source venv/bin/activate
```

### **Step 4: Check current status**
```bash
sudo systemctl status healthyrizz
```

### **Step 5: Stop the service**
```bash
sudo systemctl stop healthyrizz
```

### **Step 6: Fix the template error**
The error is in `templates/base.html` line 17. Edit the file:

```bash
nano templates/base.html
```

Find this line:
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

Change it to:
```html
<meta name="csrf-token" content="{{ csrf_token() if csrf_token else '' }}">
```

Save and exit (Ctrl+X, Y, Enter)

### **Step 7: Fix other template files**
```bash
# Fix admin base template
nano templates/admin/base_admin.html
```

Find any instances of `{{ csrf_token() }}` and change them to `{{ csrf_token() if csrf_token else '' }}`

### **Step 8: Test the application**
```bash
# Test if the app can start
python -c "from app import create_app; app = create_app(); print('✅ App created successfully')"
```

### **Step 9: Restart the service**
```bash
sudo systemctl start healthyrizz
sudo systemctl status healthyrizz
```

### **Step 10: Check the logs**
```bash
sudo journalctl -u healthyrizz -f
```

### **Step 11: Test the website**
Visit: https://healthyrizz.in

## 🔍 **If you still get errors:**

### **Check the database**
```bash
# Initialize database if needed
python init_database.py
```

### **Check file permissions**
```bash
# Make sure files are readable
chmod 644 *.py
chmod 644 templates/*.html
chmod 644 templates/admin/*.html
```

### **Check the wsgi.py file**
```bash
cat wsgi.py
```

Should contain:
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

## 🚨 **Emergency Fix (if nothing else works):**

### **Create a simple wsgi.py**
```bash
cat > wsgi.py << 'EOF'
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
EOF
```

### **Create a simple app.py backup**
```bash
cp app.py app.py.backup
```

### **Restart everything**
```bash
sudo systemctl restart healthyrizz
sudo systemctl status healthyrizz
```

## 📊 **Monitoring Commands:**

```bash
# Check service status
sudo systemctl status healthyrizz

# Check logs
sudo journalctl -u healthyrizz -n 50

# Check if port 8000 is listening
netstat -tlnp | grep 8000

# Test the application directly
curl -I http://localhost:8000
```

## ✅ **Success Indicators:**

- Service status shows "active (running)"
- No errors in journalctl logs
- Website loads without template errors
- Port 8000 is listening

## 🆘 **If you need to completely reset:**

```bash
# Stop service
sudo systemctl stop healthyrizz

# Backup current files
cp -r /home/healthyrizz/htdocs/healthyrizz.in /home/healthyrizz/htdocs/healthyrizz.in.backup

# Upload fresh files from your local machine
# Then restart
sudo systemctl start healthyrizz
``` 