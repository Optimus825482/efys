# 🐳 EFYS Docker - Hızlı Başlangıç

## ⚡ 1 Komut Kurulum

```bash
curl -sSL https://raw.githubusercontent.com/Optimus825482/efys/main/docker-deploy.sh | sudo bash
```

**Bu komut:**
- ✅ Docker + Docker Compose kurar
- ✅ EFYS'i GitHub'dan indirir
- ✅ Environment ayarları yapar
- ✅ Tüm servisleri başlatır

**Süre:** ~5 dakika

---

## 📦 Manuel Kurulum

### 1. Docker Kur
```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 2. Kodu İndir
```bash
git clone https://github.com/Optimus825482/efys.git /opt/efys
cd /opt/efys
```

### 3. Yapılandır
```bash
cp .env.docker.example .env
nano .env  # SECRET_KEY, şifreler
```

### 4. Başlat
```bash
docker-compose up -d
```

### 5. Kontrol
```bash
docker-compose ps
curl http://localhost/health
```

---

## 🎯 Sonrası - Yararlı Komutlar

```bash
# Log izle
docker-compose logs -f

# Yeniden başlat
docker-compose restart

# Durdur
docker-compose down

# Güncelle
git pull && docker-compose up -d --build

# Backup
./docker-backup.sh
```

---

## 🌐 Erişim

**HTTP:** http://your-server-ip  
**Status:** `docker-compose ps`  
**Logs:** `docker-compose logs -f app`

---

## 📚 Daha Fazlası

[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Detaylı rehber

---

**🚀 EFYS Docker'da Çalışıyor!**
