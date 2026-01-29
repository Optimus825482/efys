#!/usr/bin/env python3
"""
EFYS Health Check Script
Monitoring ve alerting için kullanılır
"""
import sys
import os
import psycopg2
from datetime import datetime
import requests

# Configuration
APP_URL = os.getenv('APP_URL', 'http://localhost:8000')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'efys_production')
DB_USER = os.getenv('DB_USER', 'efys_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'secure_password')

class HealthCheck:
    def __init__(self):
        self.status = True
        self.errors = []
        
    def check_app(self):
        """Application HTTP check"""
        try:
            response = requests.get(f"{APP_URL}/health", timeout=5)
            if response.status_code != 200:
                self.errors.append(f"❌ App HTTP check failed: {response.status_code}")
                self.status = False
            else:
                print("✅ Application responding")
        except Exception as e:
            self.errors.append(f"❌ App connection failed: {str(e)}")
            self.status = False
            
    def check_database(self):
        """Database connection check"""
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=5
            )
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            print("✅ Database connection OK")
        except Exception as e:
            self.errors.append(f"❌ Database connection failed: {str(e)}")
            self.status = False
            
    def check_disk_space(self):
        """Disk space check (min 10% free)"""
        try:
            stat = os.statvfs('/')
            free_percent = (stat.f_bavail / stat.f_blocks) * 100
            if free_percent < 10:
                self.errors.append(f"⚠️  Low disk space: {free_percent:.1f}% free")
                self.status = False
            else:
                print(f"✅ Disk space OK: {free_percent:.1f}% free")
        except Exception as e:
            self.errors.append(f"❌ Disk check failed: {str(e)}")
            
    def check_log_files(self):
        """Check if log files are writable"""
        log_dir = '/var/log/efys'
        if os.path.exists(log_dir):
            if os.access(log_dir, os.W_OK):
                print("✅ Log directory writable")
            else:
                self.errors.append(f"❌ Log directory not writable: {log_dir}")
                self.status = False
        else:
            self.errors.append(f"❌ Log directory not found: {log_dir}")
            self.status = False
            
    def run(self):
        """Run all checks"""
        print(f"\n{'='*50}")
        print(f"EFYS Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        self.check_app()
        self.check_database()
        self.check_disk_space()
        self.check_log_files()
        
        print(f"\n{'='*50}")
        if self.status:
            print("✅ All checks passed")
            print(f"{'='*50}\n")
            return 0
        else:
            print("❌ Health check failed:")
            for error in self.errors:
                print(f"  {error}")
            print(f"{'='*50}\n")
            return 1

if __name__ == '__main__':
    checker = HealthCheck()
    sys.exit(checker.run())
