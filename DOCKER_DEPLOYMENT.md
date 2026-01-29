# 🐳 EFYS Docker Deployment - Coofy Sunucu

## 🚀 Tek Komut Kurulum

```bash
# Root kullanıcı olarak
curl -sSL https://raw.githubusercontent.com/Optimus825482/efys/main/docker-deploy.sh | sudo bash
```

Bu komut otomatik olarak:
- ✅ Docker ve Docker Compose kurar
- ✅ EFYS repository'sini clone eder
- ✅ Environment variables oluşturur
- ✅ Database, Redis, App ve Nginx container'larını başlatır

---

## 📋 Manuel Kurulum

### 1. Ön Gereksinimler

```bash
# Docker kurulumu
curl -fsSL https://get.docker.com | sudo sh
sudo systemctl enable docker
sudo systemctl start docker

# Docker Compose kurulumu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Versiyonları kontrol et
docker --version
docker-compose --version
```

### 2. Repository Clone

```bash
# Uygulama dizini oluştur
sudo mkdir -p /opt/efys
cd /opt/efys

# GitHub'dan clone et
git clone https://github.com/Optimus825482/efys.git .
```

### 3. Environment Yapılandırması

```bash
# .env dosyası oluştur
cp .env.docker.example .env
nano .env
```

**Önemli değişkenler:**
```bash
SECRET_KEY=your-generated-secret-key-32-chars
DB_PASSWORD=strong-database-password
REDIS_PASSWORD=strong-redis-password
GENERATE_DEMO_DATA=true  # İlk kurulumda
```

**SECRET_KEY generate et:**
```bash
openssl rand -hex 32
```

### 4. Container'ları Başlat

```bash
# Build ve start
docker-compose build
docker-compose up -d

# Logları izle
docker-compose logs -f
```

### 5. Health Check

```bash
# Container durumları
docker-compose ps

# Uygulama erişimi test et
curl http://localhost/health

# Database bağlantısı test et
docker-compose exec app python -c "from services.database import DatabaseService; db = DatabaseService(); print('✅ DB OK'); db.close()"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Internet                                               │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Nginx Container (Port 80/443)                          │
│  - Reverse Proxy                                        │
│  - Static Files                                         │
│  - SSL Termination                                      │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  EFYS App Container (Port 8000)                         │
│  - Python 3.10                                          │
│  - Flask + Gunicorn                                     │
│  - Business Logic                                       │
└──────────┬────────────────────────────┬─────────────────┘
           │                            │
           ▼                            ▼
┌─────────────────────┐    ┌─────────────────────────────┐
│  PostgreSQL         │    │  Redis                      │
│  Container          │    │  Container                  │
│  - Database         │    │  - Session Store            │
│  - Persistent Data  │    │  - Cache                    │
└─────────────────────┘    └─────────────────────────────┘

Networks: efys-network (bridge)
Volumes: postgres_data, redis_data, nginx_logs
```

---

## 📦 Container'lar

### 1. efys-app (Application)
- **Image:** Custom (Dockerfile)
- **Port:** 8000 (internal)
- **Volumes:** uploads/, logs/
- **Health:** `curl http://localhost:8000/health`

### 2. efys-postgres (Database)
- **Image:** postgres:15-alpine
- **Port:** 5432 (localhost only)
- **Volume:** postgres_data
- **Health:** `pg_isready`

### 3. efys-redis (Cache)
- **Image:** redis:7-alpine
- **Port:** 6379 (localhost only)
- **Volume:** redis_data
- **Health:** `redis-cli ping`

### 4. efys-nginx (Reverse Proxy)
- **Image:** nginx:1.25-alpine
- **Ports:** 80, 443
- **Volumes:** static/, uploads/, nginx.conf
- **Health:** `wget http://localhost/health`

---

## 🔧 Yönetim Komutları

### Container Management
```bash
# Tüm servisleri başlat
docker-compose up -d

# Belirli servisi başlat
docker-compose up -d app

# Logları izle
docker-compose logs -f
docker-compose logs -f app      # Sadece app
docker-compose logs --tail=100  # Son 100 satır

# Container durumu
docker-compose ps
docker-compose top

# Yeniden başlat
docker-compose restart
docker-compose restart app

# Durdur
docker-compose stop
docker-compose down  # Stop + remove containers

# Temizlik (volumes dahil)
docker-compose down -v
```

### Uygulama Komutları
```bash
# App container'a gir
docker-compose exec app bash

# Python komutları çalıştır
docker-compose exec app python scripts/apply_schema.py
docker-compose exec app python scripts/generate_demo_readings.py

# Database backup
docker-compose exec postgres pg_dump -U efys_user efys_production | gzip > backup-$(date +%Y%m%d).sql.gz

# Database restore
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U efys_user efys_production
```

### Resource Monitoring
```bash
# Resource kullanımı
docker stats

# Disk kullanımı
docker system df
docker volume ls

# Temizlik
docker system prune -a  # Unused images/containers
```

---

## 🔄 Güncelleme (CI/CD)

### Manuel Güncelleme
```bash
cd /opt/efys

# Yeni kodu çek
git pull origin main

# Rebuild ve restart
docker-compose build --no-cache
docker-compose up -d

# Health check
docker-compose logs -f app
```

### Zero-Downtime Update
```bash
# Blue-green deployment için
docker-compose up -d --scale app=2  # 2 instance çalıştır
docker-compose restart app          # Birini restart et
docker-compose up -d --scale app=1  # Normal'e dön
```

---

## 🛡️ Production Optimizations

### 1. Resource Limits
```yaml
# docker-compose.yml'ye ekle
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### 2. Logging Driver
```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. Restart Policy
```yaml
services:
  app:
    restart: unless-stopped
    deploy:
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

---

## 🔒 SSL/HTTPS Setup

### Let's Encrypt (Certbot)
```bash
# Certbot container ile
docker run -it --rm \
  -v /opt/efys/docker/ssl:/etc/letsencrypt \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d yourdomain.com -d www.yourdomain.com

# Nginx HTTPS config aktifleştir
# docker/nginx.conf'daki HTTPS bloğunu uncomment et
docker-compose restart nginx
```

### Auto-renewal (Cron)
```bash
# /etc/cron.d/certbot-renew
0 3 * * * docker run --rm -v /opt/efys/docker/ssl:/etc/letsencrypt certbot/certbot renew && docker-compose -f /opt/efys/docker-compose.yml restart nginx
```

---

## 📊 Monitoring

### Prometheus + Grafana (Opsiyonel)
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 🆘 Troubleshooting

### Container başlamıyor
```bash
# Detaylı log
docker-compose logs --tail=50 app

# Container inspect
docker inspect efys-app

# Health check manuel test
docker-compose exec app curl http://localhost:8000/health
```

### Database bağlantı hatası
```bash
# PostgreSQL çalışıyor mu?
docker-compose ps postgres

# Connection test
docker-compose exec postgres psql -U efys_user -d efys_production -c "SELECT 1"

# Environment kontrol
docker-compose exec app env | grep DATABASE_URL
```

### Port conflict
```bash
# Port kullanımı kontrol
sudo netstat -tulpn | grep -E '(80|443|5432|6379)'

# docker-compose.yml'de portları değiştir
# "8080:80" şeklinde
```

### Disk dolması
```bash
# Volume kullanımı
docker system df -v

# Log cleanup
docker-compose logs --tail=0 -f  # Clear logs

# Eski image'ları sil
docker image prune -a
```

---

## 📞 Support

**Dokümantasyon:**
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [EFYS Deployment Guide](DEPLOYMENT_GUIDE.md)

**Quick Links:**
- Container Logs: `docker-compose logs -f`
- Health Check: `curl http://localhost/health`
- Database Shell: `docker-compose exec postgres psql -U efys_user efys_production`

---

## ✅ Production Checklist

Deployment öncesi kontrol:

- [ ] `.env` dosyası yapılandırıldı
- [ ] SECRET_KEY ve şifreler güçlü
- [ ] Domain DNS ayarları yapıldı
- [ ] SSL sertifikası kuruldu
- [ ] Firewall yapılandırıldı (80, 443 portları)
- [ ] Backup stratejisi belirlendi
- [ ] Log rotation yapılandırıldı
- [ ] Monitoring kuruldu
- [ ] Health checks test edildi
- [ ] Resource limits ayarlandı

---

**🐳 Docker ile EFYS Production Ready!**

```bash
cd /opt/efys
docker-compose up -d
# ✅ EFYS Running on Docker!
```
