# HealthyRizz VPS Deployment Package

This package contains everything needed to deploy HealthyRizz on a VPS.

## 🚀 Quick Deployment (Automated)

1. **Upload this package to your VPS**:
   ```bash
   scp -r healthyrizz_vps_deploy root@your-vps-ip:/root/
   ```

2. **Connect to your VPS**:
   ```bash
   ssh root@your-vps-ip
   cd healthyrizz_vps_deploy
   ```

3. **Run the automated deployment**:
   ```bash
   chmod +x deploy_healthyrizz_vps.sh
   ./deploy_healthyrizz_vps.sh
   ```

## 📖 Manual Setup

See `VPS_DEPLOYMENT_GUIDE.md` for detailed manual installation instructions.

## 📦 What's Included

- ✅ Complete HealthyRizz application code
- ✅ Automated deployment script (`deploy_healthyrizz_vps.sh`)
- ✅ Comprehensive deployment guide (`VPS_DEPLOYMENT_GUIDE.md`)
- ✅ Configuration templates and requirements
- ✅ Database models and migrations
- ✅ Static files and templates
- ✅ Routes and forms

## 🔧 System Requirements

- **OS**: Ubuntu 20.04+ / Debian 10+ / CentOS 8+
- **CPU**: 2+ cores (recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 20GB minimum (SSD recommended)
- **Network**: Public IP address
- **Access**: Root or sudo privileges

## 🌐 After Deployment

### Access Your Application
- **Website**: `http://your-domain.com` or `http://your-vps-ip`
- **Admin Panel**: `http://your-domain.com/admin/dashboard`

### Default Admin Access
- **Email**: `admin@healthyrizz.in`
- **Password**: `admin123`

> **⚠️ Important**: Change the default password after first login!

## 🛠️ Post-Deployment Commands

```bash
# Check service status
systemctl status healthyrizz

# View application logs
journalctl -u healthyrizz -f

# Restart application
systemctl restart healthyrizz

# Check nginx status
systemctl status nginx

# View nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 🔒 Security Checklist

After deployment, make sure to:
- [ ] Change default admin password
- [ ] Update `.env` file with secure keys
- [ ] Configure SSL certificate (Let's Encrypt)
- [ ] Setup firewall (UFW)
- [ ] Configure regular backups
- [ ] Update environment variables
- [ ] Setup monitoring

## 🎯 Features Included

### Admin Panel Features
- ✅ Dashboard with statistics
- ✅ User management
- ✅ Meal plan management
- ✅ Order management
- ✅ Subscription management
- ✅ Blog management
- ✅ FAQ management
- ✅ Contact inquiries
- ✅ Banner management
- ✅ Coupon system
- ✅ Newsletter management

### Frontend Features
- ✅ Responsive meal plan showcase
- ✅ User registration and login
- ✅ Meal calculator
- ✅ Contact forms
- ✅ Blog system
- ✅ FAQ section
- ✅ Mobile-optimized design

## 📞 Support

For deployment issues:
1. Check the troubleshooting section in `VPS_DEPLOYMENT_GUIDE.md`
2. View application logs: `journalctl -u healthyrizz -f`
3. Check service status: `systemctl status healthyrizz nginx postgresql redis`

## 🎉 Success!

Once deployed, your HealthyRizz meal delivery platform will be live and ready to serve customers!

Happy meal planning! 🍽️ 