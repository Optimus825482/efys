# 🚀 EFYS Production Deployment Checklist

## Pre-Deployment

### 1. Local Preparation
- [ ] Tüm testler geçiyor (`python test_all_endpoints.py`)
- [ ] Kod GitHub/GitLab'a push'landı
- [ ] `.env.example` dosyası güncel
- [ ] `requirements.txt` güncel
- [ ] `DEPLOYMENT_GUIDE.md` okundu

### 2. Server Requirements
- [ ] Ubuntu 20.04+ / Debian 11+ kurulu
- [ ] Root/sudo erişimi mevcut
- [ ] Python 3.10+ kurulu (veya kurulacak)
- [ ] PostgreSQL 13+ kurulu (veya kurulacak)
- [ ] Nginx kurulu (veya kurulacak)
- [ ] Domain A kaydı sunucu IP'sine işaret ediyor

---

## Deployment Steps

### 3. File Transfer
- [ ] Dosyalar sunucuya transfer edildi (`/tmp/efys-deploy/` veya `/var/www/efys/`)
- [ ] Script'ler executable yapıldı (`chmod +x deploy.sh backup.sh`)

**Komutlar:**
```bash
# WinSCP, scp veya git clone kullan
scp -r d:\OSOSDEMO/* root@server:/tmp/efys-deploy/
# veya
git clone https://github.com/your-repo/efys.git /var/www/efys
```

### 4. Automated Deployment
- [ ] Deployment script çalıştırıldı
- [ ] Hata olmadan tamamlandı
- [ ] PostgreSQL database oluşturuldu
- [ ] Python virtual environment kuruldu
- [ ] Dependencies yüklendi

**Komut:**
```bash
cd /tmp/efys-deploy  # veya /var/www/efys
sudo ./deploy.sh
```

### 5. Environment Configuration
- [ ] `.env` dosyası oluşturuldu (`cp .env.example .env`)
- [ ] `SECRET_KEY` generate edildi ve girildi
- [ ] `DATABASE_URL` güncellendi
- [ ] Database şifresi güçlü (16+ karakter)
- [ ] `FLASK_ENV=production` ayarlandı
- [ ] `.env` permission: 600 (`chmod 600 .env`)

**SECRET_KEY Generate:**
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

### 6. Database Setup
- [ ] PostgreSQL user oluşturuldu
- [ ] Database oluşturuldu
- [ ] Schema uygulandı (`python scripts/apply_schema.py`)
- [ ] Demo data yüklendi (opsiyonel)
- [ ] Database connection test edildi

**Test:**
```bash
psql -U efys_user -d efys_production -h localhost
\dt  # Table'ları listele
\q
```

### 7. Nginx Configuration
- [ ] Config dosyası kopyalandı (`/etc/nginx/sites-available/efys`)
- [ ] Symlink oluşturuldu (`/etc/nginx/sites-enabled/efys`)
- [ ] Domain adı güncellendi (`server_name`)
- [ ] Nginx syntax check edildi (`nginx -t`)
- [ ] Nginx reload edildi (`systemctl reload nginx`)

**Domain Değiştir:**
```bash
nano /etc/nginx/sites-available/efys
# server_name yourdomain.com www.yourdomain.com;
```

### 8. SSL Certificate (Let's Encrypt)
- [ ] Certbot kurulu
- [ ] SSL sertifikası alındı
- [ ] HTTPS redirect aktif
- [ ] Auto-renewal test edildi (`certbot renew --dry-run`)

**SSL Kurulum:**
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 9. Systemd Service
- [ ] Service dosyası kopyalandı (`/etc/systemd/system/efys.service`)
- [ ] Daemon reload edildi
- [ ] Service enable edildi
- [ ] Service başlatıldı
- [ ] Status check yapıldı

**Komutlar:**
```bash
systemctl daemon-reload
systemctl enable efys
systemctl start efys
systemctl status efys
```

---

## Post-Deployment

### 10. Testing & Verification
- [ ] Health check endpoint çalışıyor (`curl http://localhost/health`)
- [ ] Web arayüzü açılıyor (`https://yourdomain.com`)
- [ ] Login çalışıyor
- [ ] Dashboard veriler gösteriyor
- [ ] Portal abone seçim modal açılıyor
- [ ] Database queries çalışıyor
- [ ] Static files yükleniyor
- [ ] Mobile responsive çalışıyor

**Test Komutları:**
```bash
curl http://localhost/health
curl https://yourdomain.com
python3 healthcheck.py
```

### 11. Security Hardening
- [ ] Firewall yapılandırıldı (UFW)
- [ ] SSH root login kapatıldı
- [ ] SSH key-based auth aktif
- [ ] Fail2Ban kuruldu ve yapılandırıldı
- [ ] PostgreSQL external access kapalı
- [ ] `.env` dosyası chmod 600
- [ ] Sensitive files git'te yok (`.gitignore` kontrol)

**Firewall:**
```bash
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

### 12. Monitoring & Logging
- [ ] Log directory oluşturuldu (`/var/log/efys/`)
- [ ] Log rotation yapılandırıldı (`/etc/logrotate.d/efys`)
- [ ] Healthcheck script test edildi
- [ ] Cron job eklendi (healthcheck)
- [ ] Error alerting ayarlandı (opsiyonel)

**Cron Health Check:**
```bash
crontab -e
# Her 5 dakikada health check
*/5 * * * * /usr/bin/python3 /var/www/efys/healthcheck.py >> /var/log/efys/healthcheck.log 2>&1
```

### 13. Backup Configuration
- [ ] Backup script test edildi (`./backup.sh`)
- [ ] Backup directory oluşturuldu (`/var/backups/efys/`)
- [ ] Cron job eklendi (daily backup)
- [ ] Backup retention ayarlandı (30 gün)
- [ ] Restore procedure dokümante edildi

**Cron Backup:**
```bash
crontab -e
# Her gece 02:00'da backup
0 2 * * * /var/www/efys/backup.sh >> /var/log/efys/backup.log 2>&1
```

### 14. Performance Tuning
- [ ] Gunicorn worker sayısı optimize edildi (CPU cores × 2 + 1)
- [ ] Database connection pool ayarlandı
- [ ] Nginx caching yapılandırıldı (static files)
- [ ] Gzip compression aktif
- [ ] Resource limits ayarlandı (systemd service)

**Worker Optimization:**
```python
# gunicorn.conf.py
import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
```

---

## Rollback Plan

### 15. Emergency Rollback
- [ ] Eski versiyon backup'ı mevcut
- [ ] Database dump alındı (pre-deployment)
- [ ] Rollback prosedürü test edildi

**Rollback Komutları:**
```bash
# Service durdur
systemctl stop efys

# Eski kodu restore et
cd /var/www
mv efys efys-failed
tar -xzf /var/backups/efys-YYYYMMDD.tar.gz

# Database restore (gerekirse)
PGPASSWORD=password psql -U efys_user -d efys_production < backup.sql

# Service başlat
systemctl start efys
systemctl status efys
```

---

## Documentation

### 16. Project Documentation
- [ ] README.md güncel
- [ ] DEPLOYMENT_GUIDE.md güncellendi
- [ ] API endpoints dokümante edildi
- [ ] Database schema dokümante edildi
- [ ] Troubleshooting guide oluşturuldu

---

## Sign-Off

### 17. Final Checks
- [ ] Stakeholder'lara demo yapıldı
- [ ] User acceptance testing tamamlandı
- [ ] Production URL paylaşıldı
- [ ] Support email/contact bilgileri güncellendi
- [ ] Monitoring dashboard erişimi verildi

### 18. Deployment Report
```
Deployment Date: _______________
Deployed By: _______________
Version: _______________
Server: _______________
Domain: _______________
Database: _______________
Status: ✅ SUCCESS / ❌ FAILED
Notes: _______________
```

---

## 📞 Emergency Contacts

**System Admin:** [Email/Phone]  
**Database Admin:** [Email/Phone]  
**DevOps Lead:** [Email/Phone]  
**Project Manager:** [Email/Phone]

---

## 📊 Metrics to Monitor

- [ ] Response time (< 200ms)
- [ ] Error rate (< 0.1%)
- [ ] Uptime (> 99.9%)
- [ ] Database connections (< 80% pool)
- [ ] Disk space (> 20% free)
- [ ] Memory usage (< 80%)
- [ ] CPU usage (< 70%)

---

## ✅ Deployment Complete!

**Date:** _____________  
**Signed:** _____________  
**Status:** 🚀 PRODUCTION

---

**Total Checklist Items:** 80+  
**Estimated Time:** 2-4 hours (first deployment)  
**Support:** DEPLOYMENT_GUIDE.md
