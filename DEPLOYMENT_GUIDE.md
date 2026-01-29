# EFYS Production Deployment Guide
## Coofy Sunucusuna Kurulum Rehberi

> **Hedef Sunucu:** Coofy kurulu Ubuntu/Debian server  
> **Gereksinimler:** Python 3.10+, PostgreSQL 13+, Nginx, Systemd  
> **Kurulum Süresi:** ~15 dakika

---

## 📋 Ön Gereksinimler

### 1. Sistem Gereksinimleri
```bash
OS: Ubuntu 20.04+ / Debian 11+
RAM: Minimum 2GB (Önerilen 4GB+)
CPU: 2 Core+
Disk: 20GB+ (Database boyutuna göre artırın)
```

### 2. Yazılım Gereksinimleri
```bash
✅ Python 3.10+
✅ PostgreSQL 13+
✅ Nginx
✅ Git
✅ Supervisor (opsiyonel)
✅ Certbot (SSL için)
```

---

## 🚀 Hızlı Kurulum (Otomatik)

### Tek Komutla Kurulum
```bash
# Root kullanıcı olarak
cd /tmp
wget https://your-repo.com/deploy.sh  # veya git clone
chmod +x deploy.sh
sudo ./deploy.sh
```

Script otomatik olarak:
- ✅ Gerekli paketleri yükler
- ✅ Python virtual environment oluşturur
- ✅ PostgreSQL database'i kurar
- ✅ Systemd service'i yapılandırır
- ✅ Nginx reverse proxy'yi ayarlar
- ✅ Dosya izinlerini düzenler

---

## 🔧 Manuel Kurulum (Adım Adım)

### 1. Sunucuya Bağlanın
```bash
ssh root@your-coofy-server.com
```

### 2. Gerekli Paketleri Yükleyin
```bash
apt update && apt upgrade -y
apt install -y python3.10 python3.10-venv python3-pip \
               postgresql postgresql-contrib \
               nginx supervisor git curl certbot python3-certbot-nginx
```

### 3. Uygulama Dizinini Oluşturun
```bash
mkdir -p /var/www/efys
cd /var/www/efys

# Kodu GitHub'dan çekin
git clone https://github.com/your-repo/efys.git .

# Veya SCP ile transfer edin
# scp -r ./OSOSDEMO/* root@server:/var/www/efys/
```

### 4. Python Virtual Environment Kurun
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. PostgreSQL Database Yapılandırması
```bash
# PostgreSQL'e giriş yapın
sudo -u postgres psql

-- Database ve user oluşturun
CREATE DATABASE efys_production;
CREATE USER efys_user WITH ENCRYPTED PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE efys_production TO efys_user;
ALTER DATABASE efys_production OWNER TO efys_user;
\q
```

### 6. Environment Variables Ayarlayın
```bash
# .env.example dosyasını kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin
nano .env
```

**Önemli ayarlar:**
```bash
SECRET_KEY=your-super-secret-key-32-chars-minimum
DATABASE_URL=postgresql://efys_user:your_secure_password@localhost:5432/efys_production
FLASK_ENV=production
DEBUG=False
```

**SECRET_KEY oluşturun:**
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### 7. Database Schema'yı Uygulayın
```bash
source venv/bin/activate
export DATABASE_URL="postgresql://efys_user:your_password@localhost:5432/efys_production"
python scripts/apply_schema.py
```

### 8. Demo Veri Yükleyin (Opsiyonel)
```bash
python scripts/generate_demo_readings.py
```

### 9. Systemd Service Yapılandırması
```bash
# Service dosyasını kopyalayın
cp efys.service /etc/systemd/system/

# Service dosyasını düzenleyin (user, paths)
nano /etc/systemd/system/efys.service

# Service'i aktifleştirin
systemctl daemon-reload
systemctl enable efys
systemctl start efys

# Status kontrolü
systemctl status efys
```

### 10. Nginx Yapılandırması
```bash
# Nginx config dosyasını kopyalayın
cp nginx-efys.conf /etc/nginx/sites-available/efys

# Domain adınızı düzenleyin
nano /etc/nginx/sites-available/efys
# server_name yourdomain.com www.yourdomain.com;

# Symlink oluşturun
ln -s /etc/nginx/sites-available/efys /etc/nginx/sites-enabled/

# Default site'ı devre dışı bırakın
rm /etc/nginx/sites-enabled/default

# Nginx test edin
nginx -t

# Nginx'i reload edin
systemctl reload nginx
```

### 11. SSL Sertifikası (Let's Encrypt)
```bash
# Certbot ile SSL alın
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Otomatik yenileme testini yapın
certbot renew --dry-run
```

### 12. Dosya İzinleri
```bash
# Ownership ayarlayın
chown -R www-data:www-data /var/www/efys

# Directory permissions
chmod -R 755 /var/www/efys

# .env güvenliği
chmod 600 /var/www/efys/.env

# Log directories
mkdir -p /var/log/efys
chown -R www-data:www-data /var/log/efys
chmod 755 /var/log/efys

# Upload directory
mkdir -p /var/www/efys/uploads
chown -R www-data:www-data /var/www/efys/uploads
chmod 755 /var/www/efys/uploads

# Run directory
mkdir -p /var/run/efys
chown -R www-data:www-data /var/run/efys
```

### 13. Firewall Yapılandırması
```bash
# UFW firewall (Ubuntu)
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw enable
ufw status
```

---

## 🔍 Doğrulama ve Test

### 1. Service Status Kontrolü
```bash
# EFYS service
systemctl status efys

# Nginx status
systemctl status nginx

# PostgreSQL status
systemctl status postgresql
```

### 2. Log Kontrolü
```bash
# EFYS application logs
tail -f /var/log/efys/error.log
tail -f /var/log/efys/access.log

# Nginx logs
tail -f /var/log/nginx/efys-error.log
tail -f /var/log/nginx/efys-access.log

# Systemd logs
journalctl -u efys -f
```

### 3. Port Kontrolü
```bash
# Gunicorn port
netstat -tulpn | grep 8000

# Nginx port
netstat -tulpn | grep 80
netstat -tulpn | grep 443
```

### 4. Database Bağlantı Testi
```bash
source /var/www/efys/venv/bin/activate
cd /var/www/efys
python -c "from services.database import DatabaseService; db = DatabaseService(); print('✅ DB Connection OK'); db.close()"
```

### 5. Web Test
```bash
# Local test
curl http://localhost

# Domain test
curl https://yourdomain.com

# Health check endpoint
curl https://yourdomain.com/health
```

---

## 🔄 Güncelleme ve Bakım

### Application Güncelleme
```bash
cd /var/www/efys

# Mevcut kodu yedekleyin
tar -czf /var/backups/efys-$(date +%Y%m%d).tar.gz .

# Git'ten çekin
git pull origin main

# Dependencies güncelleyin
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Database migration (varsa)
python scripts/apply_schema.py

# Service'i restart edin
systemctl restart efys

# Kontrol edin
systemctl status efys
tail -f /var/log/efys/error.log
```

### Database Backup
```bash
# Manuel backup
./backup.sh

# Cron ile otomatik backup (her gece 02:00)
crontab -e
# Ekleyin:
0 2 * * * /var/www/efys/backup.sh >> /var/log/efys/backup.log 2>&1
```

### Log Rotation
```bash
# /etc/logrotate.d/efys dosyası oluşturun
cat > /etc/logrotate.d/efys << EOF
/var/log/efys/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    sharedscripts
    postrotate
        systemctl reload efys > /dev/null 2>&1 || true
    endscript
}
EOF
```

---

## 🛡️ Güvenlik Önerileri

### 1. Firewall Hardening
```bash
# Sadece gerekli portlar
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### 2. SSH Hardening
```bash
nano /etc/ssh/sshd_config

# Değişiklikler:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 2222  # Default port değiştir

systemctl restart sshd
```

### 3. PostgreSQL Hardening
```bash
nano /etc/postgresql/13/main/postgresql.conf

# Sadece local bağlantı
listen_addresses = 'localhost'

# Max connections
max_connections = 100

systemctl restart postgresql
```

### 4. Fail2Ban (Brute Force Protection)
```bash
apt install fail2ban

# Nginx için jail
cat > /etc/fail2ban/jail.d/nginx.conf << EOF
[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/efys-error.log
findtime = 600
bantime = 7200
maxretry = 10
EOF

systemctl restart fail2ban
```

### 5. Regular Security Updates
```bash
# Otomatik güvenlik güncellemeleri
apt install unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 📊 Monitoring ve Performans

### 1. Gunicorn Worker Sayısı
```
Kural: (2 × CPU_cores) + 1

Örnek:
- 2 core → 5 workers
- 4 core → 9 workers
- 8 core → 17 workers
```

### 2. PostgreSQL Connection Pooling
```python
# config.py - Pool ayarları
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 3600
```

### 3. Nginx Caching (Opsiyonel)
```nginx
# /etc/nginx/nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=efys_cache:10m max_size=1g inactive=60m use_temp_path=off;

# Site config'de
location /static {
    proxy_cache efys_cache;
    proxy_cache_valid 200 1d;
}
```

### 4. Application Monitoring
```bash
# htop - Resource monitoring
apt install htop
htop

# iotop - Disk I/O
apt install iotop
iotop

# nethogs - Network monitoring
apt install nethogs
nethogs
```

---

## 🆘 Sorun Giderme

### Service Başlamıyor
```bash
# Detaylı log
journalctl -u efys -n 100 --no-pager

# Permission kontrolü
ls -la /var/www/efys

# Port kullanımı
netstat -tulpn | grep 8000
```

### Database Connection Error
```bash
# PostgreSQL çalışıyor mu?
systemctl status postgresql

# Connection test
psql -U efys_user -d efys_production -h localhost

# .env kontrolü
cat /var/www/efys/.env | grep DATABASE_URL
```

### Nginx 502 Bad Gateway
```bash
# Gunicorn çalışıyor mu?
systemctl status efys

# Socket kontrolü
ls -la /var/run/efys/

# Nginx error log
tail -f /var/log/nginx/efys-error.log
```

### Permission Denied Errors
```bash
# Tüm permissions'ları sıfırla
chown -R www-data:www-data /var/www/efys
chmod -R 755 /var/www/efys
chmod 600 /var/www/efys/.env
```

---

## 📞 Destek ve İletişim

**Teknik Destek:**  
- Email: support@efys.com
- GitHub Issues: https://github.com/your-repo/efys/issues

**Dokümantasyon:**  
- API Docs: https://yourdomain.com/api/docs
- User Guide: https://yourdomain.com/docs

---

## 📝 Changelog

### v1.0.0 (2026-01-29)
- ✅ Initial production deployment
- ✅ Coofy server compatibility
- ✅ PostgreSQL integration
- ✅ Nginx reverse proxy
- ✅ SSL/TLS support
- ✅ Automated backup system

---

**🚀 EFYS Production-Ready!**
