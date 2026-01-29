# 🚀 GitHub → Coofy Otomatik Deployment Kurulumu

## 📋 İçindekiler
1. [GitHub Repository Setup](#1-github-repository-setup)
2. [Coofy Sunucu Hazırlığı](#2-coofy-sunucu-hazırlığı)
3. [GitHub Secrets Yapılandırması](#3-github-secrets-yapılandırması)
4. [İlk Deployment](#4-i̇lk-deployment)
5. [Workflow Açıklaması](#5-workflow-açıklaması)

---

## 1. GitHub Repository Setup

### 1.1. Local Git Initialization
```bash
# Windows PowerShell'de
cd d:\OSOSDEMO

# Git repository başlat
git init

# Remote repository ekle
git remote add origin https://github.com/Optimus825482/efys.git

# İlk commit
git add .
git commit -m "Initial commit - EFYS production ready"

# Main branch'e push
git branch -M main
git push -u origin main
```

### 1.2. GitHub'da Repository Oluşturma
1. https://github.com/Optimus825482/efys.git adresine git
2. Repository zaten varsa güncelle, yoksa yeni oluştur
3. Repository'yi **Private** yapmanız önerilir (güvenlik)

---

## 2. Coofy Sunucu Hazırlığı

### 2.1. İlk Kurulum (Manual)
```bash
# SSH ile sunucuya bağlan
ssh root@your-coofy-server.com

# Uygulama dizini oluştur
mkdir -p /var/www/efys
cd /var/www/efys

# GitHub'dan ilk clone
git clone https://github.com/Optimus825482/efys.git .

# Deploy script'ini çalıştır
chmod +x deploy.sh
sudo ./deploy.sh

# .env dosyasını yapılandır
nano .env
# SECRET_KEY, DATABASE_URL vb. ayarla

# Service'i başlat
systemctl start efys
systemctl enable efys
```

### 2.2. SSH Key Oluşturma (GitHub Actions için)
```bash
# Sunucuda yeni SSH key pair oluştur
ssh-keygen -t ed25519 -C "github-actions-efys" -f ~/.ssh/github_actions_efys -N ""

# Public key'i authorized_keys'e ekle
cat ~/.ssh/github_actions_efys.pub >> ~/.ssh/authorized_keys

# Private key'i kopyala (GitHub Secret'a ekleyeceğiz)
cat ~/.ssh/github_actions_efys
# Bu çıktıyı kopyala ve sakla!
```

### 2.3. Deployment User (Opsiyonel - Güvenlik için önerilir)
```bash
# Root yerine deployment için özel user
sudo adduser efys-deploy
sudo usermod -aG sudo efys-deploy

# efys-deploy için sudo izni (şifresiz)
sudo visudo
# Ekle: efys-deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart efys, /bin/systemctl status efys

# Ownership ayarla
sudo chown -R efys-deploy:efys-deploy /var/www/efys

# SSH key'i bu user için de ayarla
sudo -u efys-deploy ssh-keygen -t ed25519 -C "github-actions" -f /home/efys-deploy/.ssh/id_ed25519 -N ""
sudo cat /home/efys-deploy/.ssh/id_ed25519.pub >> /home/efys-deploy/.ssh/authorized_keys
```

---

## 3. GitHub Secrets Yapılandırması

### 3.1. GitHub'da Secrets Ekleme
1. Repository'ye git: https://github.com/Optimus825482/efys
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** butonuna tıkla

### 3.2. Gerekli Secrets

#### COOFY_HOST
- **Name:** `COOFY_HOST`
- **Value:** `your-coofy-server.com` (veya IP adresi)

#### COOFY_USERNAME
- **Name:** `COOFY_USERNAME`
- **Value:** `root` (veya `efys-deploy`)

#### COOFY_SSH_KEY
- **Name:** `COOFY_SSH_KEY`
- **Value:** Sunucuda oluşturduğunuz private key içeriği
```bash
# Sunucuda çalıştır:
cat ~/.ssh/github_actions_efys

# Tüm çıktıyı kopyala (-----BEGIN ... END----- dahil)
```

#### COOFY_PORT (Opsiyonel)
- **Name:** `COOFY_PORT`
- **Value:** `22` (default SSH portu değilse)

### 3.3. Secret Ekleme Örneği
```
Name: COOFY_SSH_KEY
Value:
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDXYWz9L7MhQX8hKQF0yq9u3h2xVB7F7g8bL...
(tüm key içeriği)
-----END OPENSSH PRIVATE KEY-----
```

---

## 4. İlk Deployment

### 4.1. GitHub'a Push
```bash
# Windows'ta
cd d:\OSOSDEMO

# Değişikliklerinizi commit edin
git add .
git commit -m "Add GitHub Actions workflow for auto-deployment"
git push origin main
```

### 4.2. Deployment İzleme
1. GitHub'da repository'ye git
2. **Actions** tab'ına tıkla
3. "Deploy to Coofy Production Server" workflow'unu izle
4. Her adımın loglarını görebilirsin

### 4.3. Manuel Tetikleme
Workflow'u manuel olarak da tetikleyebilirsin:
1. **Actions** → **Deploy to Coofy Production Server**
2. **Run workflow** butonuna tıkla
3. Branch seç (main) → **Run workflow**

---

## 5. Workflow Açıklaması

### 5.1. Otomatik Tetiklenme
```yaml
on:
  push:
    branches:
      - main      # main branch'e her push'ta
  workflow_dispatch:  # Manuel tetikleme için
```

### 5.2. Deployment Adımları

#### 1. Kod Checkout
GitHub repository'den kod çekiliyor

#### 2. Python Setup
Python 3.10 kurulumu ve dependencies yükleme

#### 3. Tests (Opsiyonel)
Endpoint testleri çalıştırılıyor

#### 4. SSH Deployment
```bash
1. Sunucuya SSH bağlantısı
2. Mevcut versiyonu backup al
3. Git pull (latest code)
4. Dependencies güncelle
5. Database migration
6. Service restart
7. Health check
```

### 5.3. Deployment Süresi
- **Ortalama:** 2-3 dakika
- **İlk deployment:** 5-7 dakika (dependencies)

---

## 6. Troubleshooting

### 6.1. "Permission denied" hatası
```bash
# Sunucuda
chmod 600 ~/.ssh/github_actions_efys
chmod 700 ~/.ssh
```

### 6.2. "Host key verification failed"
```bash
# GitHub Actions'da known_hosts problemi
# Workflow'a ekle:
- name: Add known hosts
  run: ssh-keyscan -H ${{ secrets.COOFY_HOST }} >> ~/.ssh/known_hosts
```

### 6.3. "Service restart failed"
```bash
# Sunucuda service loglarına bak
journalctl -u efys -n 50 --no-pager
systemctl status efys
```

### 6.4. GitHub Actions timeout
```yaml
# Workflow'da timeout arttır
jobs:
  deploy:
    timeout-minutes: 15  # Default: 360
```

---

## 7. İleri Düzey Yapılandırma

### 7.1. Slack/Discord Bildirim
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'EFYS Deployment: ${{ job.status }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 7.2. Rollback Mekanizması
```bash
# Sunucuda backup'tan restore
cd /var/www
sudo systemctl stop efys
rm -rf efys
tar -xzf /var/backups/efys-20260129-143052.tar.gz -C efys/
sudo systemctl start efys
```

### 7.3. Blue-Green Deployment
```bash
# İki ayrı directory kullan
/var/www/efys-blue
/var/www/efys-green

# Nginx'de symlink ile switch
ln -sf /var/www/efys-blue /var/www/efys-current
```

---

## 8. Güvenlik Best Practices

### ✅ Yapılması Gerekenler
- [ ] SSH key'i sadece GitHub Actions için kullan
- [ ] Repository'yi Private yap
- [ ] Secrets'ları asla commit'leme
- [ ] Deployment user kullan (root yerine)
- [ ] Firewall'da sadece gerekli portları aç
- [ ] SSH port'unu değiştir (22 → custom)
- [ ] Fail2Ban kur

### ❌ Yapılmaması Gerekenler
- [ ] `.env` dosyasını git'e ekleme
- [ ] SSH şifresini secrets'a ekleme (key kullan)
- [ ] Production DB şifresini workflow'da gösterme
- [ ] Public repository'de secrets kullanma

---

## 9. Monitoring ve Alerting

### 9.1. Deployment Status Badge
GitHub README'ye ekle:
```markdown
![Deploy Status](https://github.com/Optimus825482/efys/actions/workflows/deploy-production.yml/badge.svg)
```

### 9.2. Health Check Monitoring
```yaml
# .github/workflows/health-check.yml
name: Health Check
on:
  schedule:
    - cron: '*/5 * * * *'  # Her 5 dakikada
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check EFYS Health
        run: |
          curl -f https://yourdomain.com/health || exit 1
```

---

## 10. Quick Commands

### Local Development → Production
```bash
# 1. Test locally
python app.py

# 2. Commit changes
git add .
git commit -m "Feature: Add new dashboard widget"

# 3. Push to GitHub (auto-deploy)
git push origin main

# 4. Watch deployment
# GitHub → Actions → Latest run
```

### Emergency Rollback
```bash
# SSH to server
ssh root@your-server

# List backups
ls -lh /var/backups/efys-*

# Restore
cd /var/www
systemctl stop efys
rm -rf efys
tar -xzf /var/backups/efys-YYYYMMDD-HHMMSS.tar.gz
systemctl start efys
```

---

## 📞 Support

**GitHub Actions Docs:** https://docs.github.com/en/actions  
**SSH Action:** https://github.com/appleboy/ssh-action  
**EFYS Deployment:** DEPLOYMENT_GUIDE.md

---

## ✅ Deployment Checklist

Kurulum öncesi kontrol listesi:

- [ ] GitHub repository oluşturuldu
- [ ] Coofy sunucusunda ilk kurulum yapıldı
- [ ] SSH key oluşturuldu
- [ ] GitHub Secrets eklendi (COOFY_HOST, COOFY_USERNAME, COOFY_SSH_KEY)
- [ ] Workflow dosyaları commit edildi
- [ ] İlk push testi yapıldı
- [ ] Deployment başarılı oldu
- [ ] Health check geçti
- [ ] Production site erişilebilir

---

**🎉 Artık her `git push` ile otomatik deployment!**

```bash
git add .
git commit -m "Update feature"
git push origin main
# 🚀 Auto-deployment başladı!
```
