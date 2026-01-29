# EFYS - Production Deployment Paketini Sunucuya Yükleme

## Windows'tan Linux Sunucusuna Transfer

### 1. WinSCP ile Transfer (Tavsiye Edilen)

1. **WinSCP'yi İndirin:** https://winscp.net/eng/download.php
2. **Sunucuya Bağlanın:**
   - Host: your-coofy-server.com
   - Port: 22
   - Username: root
   - Password: [şifreniz]

3. **Dosyaları Transfer Edin:**
   - Sol panel (Local): `d:\OSOSDEMO`
   - Sağ panel (Remote): `/tmp/efys-deploy/`
   - Tüm dosyaları sürükle-bırak ile transfer edin

4. **PuTTY ile Sunucuya Bağlanın:**
```bash
ssh root@your-coofy-server.com
```

5. **Script'leri Çalıştırılabilir Yapın:**
```bash
cd /tmp/efys-deploy
chmod +x deploy.sh backup.sh
```

6. **Kurulumu Başlatın:**
```bash
sudo ./deploy.sh
```

---

### 2. Git ile Transfer (Alternatif)

#### GitHub'a Push
```bash
# Windows'ta PowerShell
cd d:\OSOSDEMO
git init
git add .
git commit -m "EFYS Production Ready"
git remote add origin https://github.com/your-username/efys.git
git push -u origin main
```

#### Sunucudan Pull
```bash
# Linux sunucuda
cd /var/www
git clone https://github.com/your-username/efys.git
cd efys
chmod +x deploy.sh backup.sh
sudo ./deploy.sh
```

---

### 3. PowerShell SCP Komutu (Windows 10+)

```powershell
# PowerShell'i Yönetici olarak açın
cd d:\OSOSDEMO

# Dosyaları transfer et
scp -r * root@your-server:/tmp/efys-deploy/

# Sunucuya bağlan ve kur
ssh root@your-server
cd /tmp/efys-deploy
chmod +x deploy.sh backup.sh
sudo ./deploy.sh
```

---

## Kurulum Sonrası Yapılacaklar

### 1. Environment Variables
```bash
cd /var/www/efys
nano .env
```

**Mutlaka değiştirin:**
```bash
SECRET_KEY=[python3 -c 'import secrets; print(secrets.token_hex(32))' komutu çıktısı]
DATABASE_URL=postgresql://efys_user:[güçlü_şifre]@localhost:5432/efys_production
```

### 2. Nginx Domain Ayarı
```bash
nano /etc/nginx/sites-available/efys
```

**Değiştir:**
```nginx
server_name yourdomain.com www.yourdomain.com;
```

**SSL Ekle:**
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Servisleri Başlat
```bash
systemctl start efys
systemctl status efys
systemctl reload nginx
```

### 4. Test Et
```bash
# Health check
curl http://localhost/health

# Database connection
python3 healthcheck.py

# Web tarayıcı
# https://yourdomain.com
```

---

## Dosya Listesi

### Core Files
- `app.py` - Flask application entry point
- `config.py` - Application configuration
- `requirements.txt` - Python dependencies

### Deployment Files (YENİ)
- `.env.example` - Environment template
- `gunicorn.conf.py` - WSGI server config
- `efys.service` - Systemd service
- `nginx-efys.conf` - Nginx config
- `deploy.sh` - Auto-deployment script ⭐
- `backup.sh` - Backup script
- `healthcheck.py` - Monitoring script
- `.gitignore` - Security patterns

### Documentation (YENİ)
- `DEPLOYMENT_GUIDE.md` - Detaylı rehber (500+ satır)
- `QUICKSTART_DEPLOYMENT.md` - Hızlı başlangıç
- `TRANSFER_INSTRUCTIONS.md` - Bu dosya

---

## Güvenlik Notları

### ⚠️ Asla Git'e Eklemeyin
- `.env` dosyası
- Database şifreleri
- SSL private key'ler
- Backup dosyaları
- Log dosyaları

### ✅ Mutlaka Yapın
- SECRET_KEY değiştirin
- Database şifresi değiştirin
- .env dosyasını chmod 600 yapın
- SSL sertifikası kurun
- Firewall yapılandırın
- Fail2Ban kurun

---

## Sorun Giderme

### "Permission denied" hatası
```bash
chmod +x deploy.sh backup.sh
sudo ./deploy.sh
```

### "Port already in use"
```bash
# 8000 portunu kullanan process'i bulun
sudo netstat -tulpn | grep 8000
sudo kill -9 [PID]
```

### "Database connection failed"
```bash
# PostgreSQL çalışıyor mu?
systemctl status postgresql

# Şifre doğru mu?
psql -U efys_user -d efys_production -h localhost
```

### "Nginx 502 Bad Gateway"
```bash
# EFYS service çalışıyor mu?
systemctl status efys

# Log kontrol
tail -f /var/log/efys/error.log
```

---

## İletişim

**Teknik Destek:** support@efys.com  
**Dokümantasyon:** DEPLOYMENT_GUIDE.md  
**GitHub Issues:** https://github.com/your-repo/efys/issues

---

**🚀 Başarılı Deployment'lar!**
