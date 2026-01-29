# 🚀 HIZLI BAŞLANGIÇ - GitHub → Coofy Otomatik Deployment

## ⚡ 3 Basit Adım

### 1️⃣ GitHub'a Push (İlk Kez)
```powershell
# Windows PowerShell
cd d:\OSOSDEMO
.\PUSH_TO_GITHUB.ps1
```

Veya manuel:
```bash
git init
git remote add origin https://github.com/Optimus825482/efys.git
git add .
git commit -m "Initial commit - EFYS ready"
git push -u origin main
```

### 2️⃣ GitHub Secrets Ekle
GitHub'da → **Settings** → **Secrets** → **Actions** → **New secret**

| Secret Name | Value |
|------------|-------|
| `COOFY_HOST` | `your-server-ip` veya `domain.com` |
| `COOFY_USERNAME` | `root` (veya deploy user) |
| `COOFY_SSH_KEY` | Sunucudaki private key içeriği |

**SSH Key Alma (Sunucuda):**
```bash
ssh root@your-server
ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_actions  # Bunu GitHub Secret'a ekle
```

### 3️⃣ İlk Deployment (Manuel - Sunucuda)
```bash
ssh root@your-server
mkdir -p /var/www/efys
cd /var/www/efys
git clone https://github.com/Optimus825482/efys.git .
chmod +x deploy.sh
sudo ./deploy.sh
nano .env  # SECRET_KEY, DATABASE_URL ayarla
systemctl start efys
```

---

## ✅ Hazır! Artık Otomatik

Her `git push` sonrası:
1. GitHub Actions tetikleniyor
2. Testler çalışıyor
3. Coofy sunucuya SSH ile bağlanıyor
4. Kod güncelleniyor
5. Service yeniden başlatılıyor
6. Health check yapılıyor

**⏱️ Süre:** ~2-3 dakika

---

## 📊 Deployment İzleme

**GitHub Actions:**  
https://github.com/Optimus825482/efys/actions

**Sunucu Logları:**
```bash
ssh root@your-server
journalctl -u efys -f
tail -f /var/log/efys/error.log
```

---

## 🔄 Günlük Kullanım

```powershell
# Kod değiştir
# ...

# Push et (otomatik deploy)
git add .
git commit -m "Feature: Yeni dashboard widget"
git push origin main

# GitHub Actions'da izle
# https://github.com/Optimus825482/efys/actions
```

---

## 📚 Detaylı Dokümantasyon

- **Kurulum Rehberi:** [GITHUB_DEPLOYMENT_SETUP.md](GITHUB_DEPLOYMENT_SETUP.md)
- **Production Deployment:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Hızlı Başlangıç:** [QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md)

---

## 🆘 Sorun Giderme

### "Permission denied (publickey)"
```bash
# SSH key'i GitHub Secret'a doğru eklenmiş mi?
# Sunucuda authorized_keys'e eklenmiş mi?
ssh -i ~/.ssh/github_actions root@your-server  # Test et
```

### Deployment başarısız
```bash
# GitHub Actions'da log'lara bak
# Sunucuda service status
systemctl status efys
journalctl -u efys -n 50 --no-pager
```

### Service başlamıyor
```bash
# .env kontrol
cat /var/www/efys/.env

# Database bağlantı test
cd /var/www/efys
source venv/bin/activate
python -c "from services.database import DatabaseService; DatabaseService().close()"
```

---

**🎉 Otomatik Deployment Aktif!**
