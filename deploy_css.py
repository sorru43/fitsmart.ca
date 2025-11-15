#!/usr/bin/env python3
"""
Deployment script for HealthyRizz CSS
Run this on your VPS to bundle CSS and restart the service
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def deploy_css():
    """Deploy CSS changes to VPS"""
    print("🚀 HealthyRizz CSS Deployment")
    print("=" * 40)
    
    # Step 1: Bundle CSS
    if not run_command("python3 build_css.py", "Bundling CSS"):
        return False
    
    # Step 2: Restart Flask service
    if not run_command("sudo systemctl restart healthyrizz", "Restarting Flask service"):
        return False
    
    # Step 3: Check service status
    if not run_command("sudo systemctl status healthyrizz", "Checking service status"):
        return False
    
    print("\n🎉 Deployment completed successfully!")
    print("🌐 Your website should now be using the bundled CSS")
    print("💡 Visit: https://healthyrizz.in")
    
    return True

if __name__ == "__main__":
    if deploy_css():
        sys.exit(0)
    else:
        sys.exit(1) 