# 🚀 EFYS Coolify Deployment Guide

## ✅ Veritabanı Bağlantı Kontrolü

**Bağlantı Durumu:** ✅ BAŞARILI

**Database Details:**

- Host: 77.42.68.4
- Port: 5436
- Database: osos_db
- User: postgres
- Tablolar: 24 tablo (tüm gerekli tablolar mevcut)

**Health Status:**

- ✅ Connection: 11 aktif bağlantı
- ✅ Cache Hit Rate: %100
- ✅ Constraints: Geçerli
- ✅ Vacuum: Sağlıklı

---

## 📋 Coolify Deployment Adımları

### 1. Coolify'da Yeni Proje Oluştur

1. Coolify Dashboard'a giriş yap
2. **New Resource** → **Application** seç
3. **Git Repository** seç
4. Repository URL'ini gir veya GitHub'dan seç

### 2. Build Configuration

**Build Pack:** Dockerfile

**Dockerfile Path:** `./Dockerfile`

**Build Command:** (Otomatik - Dockerfile'dan alınır)

### 3. Environment Variables

Coolify'da **Environment** sekmesine git ve şu değişkenleri ekle:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production

# Security (ÖNEMLİ: Bu değeri değiştir!)
SECRET_KEY=efys-coolify-production-secret-key-2026-change-this

# Database (External PostgreSQL)
DATABASE_URL=postgresql://postgres:518518Erkan@77.42.68.4:5436/osos_db

# Application
APP_NAME=EFYS
APP_VERSION=1.0.0

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
GUNICORN_BIND=0.0.0.0:8000

# Session
SESSION_COOKIE_SECURE=true
PERMANENT_SESSION_LIFETIME=86400

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/app/uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/efys.log

# Timezone
TZ=Europe/Istanbul
```

**💡 Alternatif:** `.env.coolify` dosyasını Coolify'a yükle

### 4. Port Configuration

**Application Port:** 8000

**Public Port:** 80 (veya 443 SSL için)

### 5. Health Check

**Health Check Path:** `/health`

**Health Check Interval:** 30s

**Health Check Timeout:** 10s

### 6. Persistent Storage (Volumes)

Coolify'da **Storage** sekmesine git:

**Volume 1 - Uploads:**

- Source: `/app/uploads`
- Destination: Coolify managed volume
- Size: 5GB

**Volume 2 - Logs:**

- Source: `/app/logs`
- Destination: Coolify managed volume
- Size: 1GB

### 7. Domain Configuration

**Domain:** efys.yourdomain.com

**SSL:** Let's Encrypt (Otomatik)

---

## 🔧 Deployment Checklist

### Pre-Deployment

- [x] Veritabanı bağlantısı test edildi
- [x] Tüm tablolar mevcut (24 tablo)
- [x] Database health check yapıldı
- [ ] SECRET_KEY production değeri ile değiştirildi
- [ ] Domain DNS ayarları yapıldı
- [ ] SSL sertifikası hazır

### Deployment

- [ ] Coolify'da proje oluşturuldu
- [ ] Environment variables eklendi
- [ ] Port configuration yapıldı
- [ ] Health check ayarlandı
- [ ] Persistent volumes oluşturuldu
- [ ] Domain bağlandı
- [ ] SSL aktif edildi

### Post-Deployment

- [ ] Health check endpoint test edildi (`/health`)
- [ ] Login sayfası açıldı (`/login`)
- [ ] Database bağlantısı çalışıyor
- [ ] Static files yükleniyor
- [ ] File upload çalışıyor
- [ ] Logs yazılıyor

---

## 🧪 Test Endpoints

Deploy sonrası şu endpoint'leri test et:

```bash
# Health Check
curl https://efys.yourdomain.com/health

# Login Page
curl https://efys.yourdomain.com/login

# Static Files
curl https://efys.yourdomain.com/static/css/efys.css
```

---

## 🔍 Troubleshooting

### Problem: Database Connection Error

**Çözüm:**

1. Coolify'da Environment Variables'ı kontrol et
2. Database host'un Coolify sunucusundan erişilebilir olduğunu doğrula
3. PostgreSQL firewall kurallarını kontrol et (Port 5436 açık mı?)

```bash
# Coolify container'dan test et
docker exec -it <container-id> bash
psql postgresql://postgres:518518Erkan@77.42.68.4:5436/osos_db
```

### Problem: Static Files Yüklenmiyor

**Çözüm:**

1. Dockerfile'da `COPY static /app/static` satırını kontrol et
2. Nginx reverse proxy kullanıyorsan static path'i ayarla

### Problem: File Upload Çalışmıyor

**Çözüm:**

1. `/app/uploads` volume'ünün mount edildiğini kontrol et
2. Write permission'ları kontrol et
3. MAX_CONTENT_LENGTH değerini kontrol et

### Problem: Application Crash

**Çözüm:**

1. Coolify logs'u kontrol et
2. Gunicorn worker sayısını azalt (GUNICORN_WORKERS=2)
3. Memory limit'i artır

---

## 📊 Monitoring

### Coolify Built-in Monitoring

Coolify Dashboard'da:

- CPU Usage
- Memory Usage
- Network Traffic
- Container Logs

### Application Logs

```bash
# Coolify container logs
docker logs -f <container-id>

# Application logs (volume içinde)
docker exec -it <container-id> tail -f /app/logs/efys.log
```

### Database Monitoring

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'osos_db';

-- Slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## 🔄 Rollback Plan

Deployment başarısız olursa:

1. Coolify'da **Previous Deployment** seç
2. **Rollback** butonuna tıkla
3. Health check'in geçmesini bekle

---

## 🚀 Deployment Komutu

Coolify CLI kullanıyorsan:

```bash
# Deploy
coolify deploy --project efys --environment production

# Logs
coolify logs --project efys --follow

# Restart
coolify restart --project efys
```

---

## 📝 Notes

1. **Database:** External PostgreSQL kullanıyoruz (77.42.68.4:5436)
2. **Redis:** Şu an kullanılmıyor (gelecekte session store için eklenebilir)
3. **Nginx:** Coolify'ın built-in reverse proxy'si yeterli
4. **SSL:** Let's Encrypt otomatik

---

## 🎯 Production Checklist

### Security

- [ ] SECRET_KEY güçlü ve unique
- [ ] Database password güvenli
- [ ] SESSION_COOKIE_SECURE=true
- [ ] HTTPS aktif
- [ ] Firewall kuralları ayarlandı

### Performance

- [ ] Gunicorn worker sayısı optimize edildi
- [ ] Database connection pool ayarlandı
- [ ] Static files CDN'den servis ediliyor (opsiyonel)
- [ ] Gzip compression aktif

### Reliability

- [ ] Health check çalışıyor
- [ ] Auto-restart aktif
- [ ] Backup stratejisi var
- [ ] Monitoring kurulu
- [ ] Alert sistemi aktif

---

## 📞 Support

Sorun yaşarsan:

1. Coolify logs'u kontrol et
2. Database bağlantısını test et
3. Environment variables'ı doğrula
4. Health check endpoint'ini test et

**Deployment başarılı olsun! 🚀**
