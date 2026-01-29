# 📦 EFYS - Coofy Sunucu Deployment Paketi

> **EFYS (Enerji Faturalandırma ve Yönetim Sistemi)**  
> Production-ready deployment paketi - Coofy sunucusu için optimize edilmiş

---

## 🎯 Bu Pakette Neler Var?

### 📋 Core Application Files
- ✅ Flask Application (`app.py`, `config.py`)
- ✅ Database Layer (`services/database.py`)
- ✅ Routes & Blueprints (`routes/`)
- ✅ Templates (`templates/`)
- ✅ Static Assets (`static/`)

### 🚀 Deployment Files (YENİ!)
| Dosya | Açıklama |
|-------|----------|
| **deploy.sh** | 🤖 Otomatik kurulum script'i |
| **gunicorn.conf.py** | ⚙️ WSGI server konfigürasyonu |
| **efys.service** | 🔄 Systemd service tanımı |
| **nginx-efys.conf** | 🌐 Nginx reverse proxy config |
| **backup.sh** | 💾 Database & files backup script |
| **healthcheck.py** | 🏥 System health monitoring |
| **.env.example** | 🔐 Environment variables template |
| **.gitignore** | 🔒 Git security patterns |

### 📚 Documentation (YENİ!)
| Dosya | Açıklama |
|-------|----------|
| **DEPLOYMENT_GUIDE.md** | 📖 500+ satır detaylı rehber |
| **QUICKSTART_DEPLOYMENT.md** | ⚡ 5 dakikalık hızlı başlangıç |
| **DEPLOYMENT_CHECKLIST.md** | ✅ 80+ maddelik kontrol listesi |
| **TRANSFER_INSTRUCTIONS.md** | 📤 Windows → Linux transfer rehberi |
| **THIS_FILE.md** | 📋 Genel bakış (şu anda okuduğunuz) |

---

## 🚀 Hızlı Kurulum (3 Adım)

### 1️⃣ Dosyaları Sunucuya Transfer Et
```bash
# WinSCP, FileZilla veya SCP ile
scp -r d:\OSOSDEMO/* root@your-server:/tmp/efys-deploy/
```

### 2️⃣ Otomatik Kurulum Çalıştır
```bash
ssh root@your-server
cd /tmp/efys-deploy
chmod +x deploy.sh
sudo ./deploy.sh
```

### 3️⃣ Yapılandır ve Başlat
```bash
# Environment ayarla
cd /var/www/efys
nano .env  # SECRET_KEY, DATABASE_URL güncelle

# Domain ayarla
nano /etc/nginx/sites-available/efys  # server_name güncelle

# SSL ekle
certbot --nginx -d yourdomain.com

# Başlat
systemctl start efys
systemctl status efys
```

**✅ HAZIR!** → https://yourdomain.com

---

## 📁 Klasör Yapısı

```
OSOSDEMO/
├── 🚀 DEPLOYMENT FILES (Production için)
│   ├── deploy.sh                    ⭐ Otomatik kurulum
│   ├── backup.sh                    💾 Backup script
│   ├── healthcheck.py               🏥 Health monitoring
│   ├── gunicorn.conf.py             ⚙️ WSGI server config
│   ├── efys.service                 🔄 Systemd service
│   ├── nginx-efys.conf              🌐 Nginx config
│   ├── .env.example                 🔐 Environment template
│   └── .gitignore                   🔒 Security patterns
│
├── 📚 DOCUMENTATION (Rehberler)
│   ├── DEPLOYMENT_GUIDE.md          📖 Detaylı rehber (500+ satır)
│   ├── QUICKSTART_DEPLOYMENT.md     ⚡ Hızlı başlangıç
│   ├── DEPLOYMENT_CHECKLIST.md      ✅ 80+ madde checklist
│   ├── TRANSFER_INSTRUCTIONS.md     📤 Transfer rehberi
│   └── README_DEPLOYMENT.md         📋 Bu dosya
│
├── 🐍 APPLICATION FILES
│   ├── app.py                       Flask entry point
│   ├── config.py                    Configuration
│   ├── requirements.txt             Python dependencies
│   ├── routes/                      Blueprint routes
│   ├── services/                    Database layer
│   ├── templates/                   Jinja2 templates
│   ├── static/                      CSS, JS, images
│   └── scripts/                     Utility scripts
│
└── 🗄️ DATABASE FILES
    └── database/
        ├── schema.sql               Database schema
        └── seed_gonen_subscribers.sql
```

---

## 🔧 Sistem Gereksinimleri

### Sunucu (Minimum)
- **OS:** Ubuntu 20.04+ / Debian 11+
- **RAM:** 2GB (4GB+ önerilir)
- **CPU:** 2 Core+
- **Disk:** 20GB+
- **Python:** 3.10+
- **PostgreSQL:** 13+

### Yazılım Stack
```
Frontend: Jinja2 + Tailwind CSS + Vanilla JS
Backend:  Flask 3.0 + Gunicorn
Database: PostgreSQL 13+ (psycopg2)
Proxy:    Nginx + SSL (Let's Encrypt)
OS:       Systemd + UFW Firewall
```

---

## 📖 Hangi Dokümanı Ne Zaman Okuyayım?

| Durum | Okumanız Gereken |
|-------|------------------|
| İlk kez kuruyorum | **QUICKSTART_DEPLOYMENT.md** (5 dk) |
| Detaylı adımlar istiyorum | **DEPLOYMENT_GUIDE.md** (15 dk) |
| Windows'tan transfer edeceğim | **TRANSFER_INSTRUCTIONS.md** (5 dk) |
| Checklist istiyorum | **DEPLOYMENT_CHECKLIST.md** (kontrol listesi) |
| Sorun giderme | **DEPLOYMENT_GUIDE.md** (Troubleshooting bölümü) |

---

## ⚡ Önemli Komutlar

### Service Yönetimi
```bash
systemctl start efys      # Başlat
systemctl stop efys       # Durdur
systemctl restart efys    # Yeniden başlat
systemctl status efys     # Durum
journalctl -u efys -f     # Canlı log
```

### Backup
```bash
./backup.sh               # Manuel backup
crontab -e                # Otomatik backup ayarla
```

### Health Check
```bash
python3 healthcheck.py    # Sistem kontrolü
curl http://localhost/health
```

### Logs
```bash
tail -f /var/log/efys/error.log       # App errors
tail -f /var/log/nginx/efys-error.log # Nginx errors
```

---

## 🛡️ Güvenlik Notları

### ⚠️ Mutlaka Yapın
1. ✅ `.env` dosyasını oluşturun ve şifreleyin (`chmod 600`)
2. ✅ `SECRET_KEY` rastgele 32+ karakter olmalı
3. ✅ PostgreSQL şifresini değiştirin
4. ✅ SSL sertifikası kurun (Let's Encrypt)
5. ✅ Firewall yapılandırın (UFW)
6. ✅ SSH root login'i kapatın
7. ✅ Fail2Ban kurun

### 🔥 Asla Yapmayın
1. ❌ `.env` dosyasını git'e eklemeyin
2. ❌ Default şifreleri kullanmayın
3. ❌ HTTP üzerinden production çalıştırmayın
4. ❌ Debug mode'u production'da aktif bırakmayın
5. ❌ Database'i external erişime açmayın

---

## 🎯 Deployment Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. TRANSFER FILES                                      │
│     Windows → Linux (WinSCP/SCP/Git)                    │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  2. RUN deploy.sh                                       │
│     • Install packages                                  │
│     • Create Python venv                                │
│     • Setup PostgreSQL                                  │
│     • Configure Systemd                                 │
│     • Setup Nginx                                       │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  3. CONFIGURE                                           │
│     • Edit .env (SECRET_KEY, DATABASE_URL)              │
│     • Edit nginx-efys.conf (server_name)                │
│     • Run certbot for SSL                               │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  4. START SERVICES                                      │
│     systemctl start efys                                │
│     systemctl reload nginx                              │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  5. VERIFY                                              │
│     • curl http://localhost/health                      │
│     • python3 healthcheck.py                            │
│     • Open https://yourdomain.com                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🐛 Sorun Giderme (Quick Fix)

### "Service başlamıyor"
```bash
journalctl -u efys -n 50 --no-pager
# Log'larda hatayı bul ve düzelt
```

### "Nginx 502 Bad Gateway"
```bash
systemctl status efys  # Service çalışıyor mu?
tail -f /var/log/efys/error.log
```

### "Database connection failed"
```bash
systemctl status postgresql
psql -U efys_user -d efys_production -h localhost
```

### "Permission denied"
```bash
chown -R www-data:www-data /var/www/efys
chmod 600 /var/www/efys/.env
```

**Daha fazlası için:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) → Troubleshooting bölümü

---

## 📞 Destek

**Dokümantasyon:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)  
**Hızlı Başlangıç:** [QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md)  
**Checklist:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)  
**Transfer:** [TRANSFER_INSTRUCTIONS.md](TRANSFER_INSTRUCTIONS.md)

**GitHub Issues:** https://github.com/your-repo/efys/issues  
**Email:** support@efys.com

---

## 🎉 Version History

### v1.0.0 (2026-01-29)
- ✅ Initial production deployment package
- ✅ Automated deployment script
- ✅ Comprehensive documentation (1000+ lines)
- ✅ Security hardening
- ✅ Backup & monitoring tools
- ✅ Coofy server optimization

---

## 📊 Deployment Stats

- **Total Files:** 9 deployment files
- **Documentation:** 4 comprehensive guides
- **Total Documentation Lines:** 1200+
- **Checklist Items:** 80+
- **Estimated Setup Time:** 15-30 minutes
- **Production Ready:** ✅ YES

---

**🚀 EFYS - Production Deployment Package**  
**Ready for Coofy Server Deployment!**

---

## Quick Links

1. [🚀 Quick Start](QUICKSTART_DEPLOYMENT.md)
2. [📖 Full Guide](DEPLOYMENT_GUIDE.md)
3. [✅ Checklist](DEPLOYMENT_CHECKLIST.md)
4. [📤 Transfer](TRANSFER_INSTRUCTIONS.md)

**Start here:** [QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md)
