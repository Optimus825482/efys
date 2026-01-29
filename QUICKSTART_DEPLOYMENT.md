# 🚀 EFYS - Coofy Sunucusuna Kurulum

## Hızlı Başlangıç (5 Dakika)

### 1️⃣ Sunucuya Bağlan
```bash
ssh root@your-coofy-server.com
```

### 2️⃣ Kodu Transfer Et
```bash
# Seçenek A: SCP ile
scp -r d:\OSOSDEMO/* root@server:/tmp/efys/

# Seçenek B: Git ile
cd /var/www
git clone https://github.com/your-repo/efys.git
```

### 3️⃣ Otomatik Kurulum
```bash
cd /tmp/efys  # veya /var/www/efys
chmod +x deploy.sh
sudo ./deploy.sh
```

### 4️⃣ Yapılandırma
```bash
cd /var/www/efys

# .env dosyasını düzenle
nano .env

# Değiştir:
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql://efys_user:your_password@localhost:5432/efys_production
```

### 5️⃣ Servisi Başlat
```bash
systemctl start efys
systemctl status efys
```

### 6️⃣ Nginx Domain Ayarla
```bash
nano /etc/nginx/sites-available/efys

# Değiştir:
server_name yourdomain.com www.yourdomain.com;

# SSL ekle (Let's Encrypt)
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Nginx reload
systemctl reload nginx
```

---

## ✅ Kurulum Tamamlandı!

Tarayıcınızdan: **https://yourdomain.com**

---

## 📁 Oluşturulan Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `.env.example` | Environment variables template |
| `gunicorn.conf.py` | Gunicorn WSGI server config |
| `efys.service` | Systemd service definition |
| `nginx-efys.conf` | Nginx reverse proxy config |
| `deploy.sh` | Otomatik deployment script |
| `backup.sh` | Database & files backup script |
| `healthcheck.py` | Monitoring health check |
| `.gitignore` | Git security patterns |
| `DEPLOYMENT_GUIDE.md` | Detaylı kurulum dokümantasyonu |

---

## 🔧 Yararlı Komutlar

### Service Yönetimi
```bash
systemctl start efys      # Başlat
systemctl stop efys       # Durdur
systemctl restart efys    # Yeniden başlat
systemctl status efys     # Durum
```

### Log İzleme
```bash
tail -f /var/log/efys/error.log       # App errors
tail -f /var/log/nginx/efys-error.log # Nginx errors
journalctl -u efys -f                 # Systemd logs
```

### Database Backup
```bash
./backup.sh                           # Manuel backup
crontab -e                            # Otomatik backup ayarla
# Ekle: 0 2 * * * /var/www/efys/backup.sh
```

### Health Check
```bash
python3 healthcheck.py                # Sistem kontrolü
curl http://localhost/health          # HTTP health endpoint
```

---

## 🛡️ Güvenlik Checklist

- [ ] `.env` dosyası oluşturuldu ve şifrelendi (chmod 600)
- [ ] SECRET_KEY rastgele 32+ karakter
- [ ] PostgreSQL şifresi değiştirildi
- [ ] Nginx domain ayarlandı
- [ ] SSL sertifikası kuruldu (Let's Encrypt)
- [ ] Firewall yapılandırıldı (ufw)
- [ ] SSH root login kapatıldı
- [ ] Fail2Ban aktif
- [ ] Backup cron job eklendi

---

## 📊 Production Checklist

- [ ] Database schema uygulandı
- [ ] Demo data yüklendi (opsiyonel)
- [ ] Static files collect edildi
- [ ] Log rotation yapılandırıldı
- [ ] Monitoring kuruldu (healthcheck.py)
- [ ] Error alerting ayarlandı
- [ ] Backup stratejisi belirlendi
- [ ] Rollback planı hazırlandı

---

## 🆘 Sorun mu Var?

**DEPLOYMENT_GUIDE.md** dosyasını inceleyin. Detaylı troubleshooting adımları içerir.

### Hızlı Sorun Giderme
```bash
# Service durumu
systemctl status efys

# Son 50 satır error log
journalctl -u efys -n 50 --no-pager

# Database bağlantısı test
psql -U efys_user -d efys_production -h localhost

# Nginx syntax check
nginx -t

# Port kullanımı
netstat -tulpn | grep -E '(8000|80|443)'
```

---

## 📞 Destek

**Dokümantasyon:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)  
**Issues:** GitHub Issues  
**Email:** support@efys.com

---

**🎉 EFYS Production'da!**
