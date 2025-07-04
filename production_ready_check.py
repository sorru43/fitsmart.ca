import subprocess
import os
from pathlib import Path

class ProductionReadyCheck:
    def check_linux_services(self):
        self.log_result('info', "=== LINUX VPS SERVICES CHECK ===")
        # Gunicorn
        try:
            out = subprocess.check_output(['systemctl', 'is-active', 'gunicorn'], stderr=subprocess.STDOUT)
            if b'active' in out:
                self.log_result('passed', "Gunicorn systemd service is running")
            else:
                self.log_result('failed', "Gunicorn systemd service is not running")
        except Exception:
            self.log_result('warnings', "Gunicorn systemd service not found or not running")

        # Supervisor
        try:
            out = subprocess.check_output(['systemctl', 'is-active', 'supervisor'], stderr=subprocess.STDOUT)
            if b'active' in out:
                self.log_result('passed', "Supervisor systemd service is running")
            else:
                self.log_result('failed', "Supervisor systemd service is not running")
        except Exception:
            self.log_result('warnings', "Supervisor systemd service not found or not running")

        # Nginx
        try:
            out = subprocess.check_output(['systemctl', 'is-active', 'nginx'], stderr=subprocess.STDOUT)
            if b'active' in out:
                self.log_result('passed', "Nginx is running")
            else:
                self.log_result('failed', "Nginx is not running")
        except Exception:
            self.log_result('warnings', "Nginx not found or not running")

        # SSL Certificate
        ssl_path = Path('/etc/letsencrypt/live')
        if ssl_path.exists() and any(ssl_path.iterdir()):
            self.log_result('passed', "Let's Encrypt SSL certificates found")
        else:
            self.log_result('warnings', "SSL certificates not found in /etc/letsencrypt/live")

        # Firewall
        try:
            out = subprocess.check_output(['ufw', 'status'], stderr=subprocess.STDOUT)
            if b'active' in out:
                self.log_result('passed', "UFW firewall is active")
            else:
                self.log_result('warnings', "UFW firewall is not active")
        except Exception:
            self.log_result('info', "UFW firewall not installed or not configured")

        # Disk usage
        st = os.statvfs('/')
        free_gb = (st.f_bavail * st.f_frsize) / 1024 / 1024 / 1024
        if free_gb < 2:
            self.log_result('warnings', f"Low disk space: {free_gb:.2f} GB free")
        else:
            self.log_result('passed', f"Disk space OK: {free_gb:.2f} GB free")

        # Swap
        try:
            out = subprocess.check_output(['swapon', '--show'], stderr=subprocess.STDOUT)
            if out.strip():
                self.log_result('passed', "Swap space is enabled")
            else:
                self.log_result('warnings', "No swap space enabled")
        except Exception:
            self.log_result('info', "Could not check swap space")

    def run_all_checks(self):
        print("🚀 HEALTHYRIZZ PRODUCTION READINESS CHECK (LINUX VPS)")
        print("=" * 50)
        self.check_python_version()
        self.check_requirements_file()
        self.check_env_file()
        self.check_database()
        self.check_payment_gateway()
        self.check_pwa_setup()
        self.check_security()
        self.check_email_setup()
        self.check_file_permissions()
        self.check_dependencies()
        self.check_production_requirements()
        self.check_linux_services()
        self.generate_report() 