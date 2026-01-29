#!/bin/bash
# EFYS Production Deployment Script
# Coofy sunucusuna otomatik kurulum

set -e  # Hata durumunda dur

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="efys"
APP_DIR="/var/www/efys"
DB_NAME="efys_production"
DB_USER="efys_user"
PYTHON_VERSION="3.10"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  EFYS Production Deployment - Coofy Server            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bu script root olarak çalıştırılmalı${NC}"
    echo "Kullanım: sudo bash deploy.sh"
    exit 1
fi

echo -e "${YELLOW}[1/10] Sistem güncellemeleri kontrol ediliyor...${NC}"
apt update -qq

echo -e "${YELLOW}[2/10] Gerekli paketler kuruluyor...${NC}"
apt install -y python3.10 python3.10-venv python3-pip postgresql nginx supervisor git curl

echo -e "${YELLOW}[3/10] Uygulama dizini oluşturuluyor...${NC}"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/uploads
mkdir -p $APP_DIR/logs
mkdir -p /var/log/$APP_NAME
mkdir -p /var/run/$APP_NAME

echo -e "${YELLOW}[4/10] Python virtual environment kuruluyor...${NC}"
cd $APP_DIR
python3.10 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}[5/10] Python dependencies yükleniyor...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}[6/10] PostgreSQL database oluşturuluyor...${NC}"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database zaten mevcut"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD 'efys_secure_password_2026';" 2>/dev/null || echo "User zaten mevcut"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

echo -e "${YELLOW}[7/10] Database schema uygulanıyor...${NC}"
export DATABASE_URL="postgresql://$DB_USER:efys_secure_password_2026@localhost:5432/$DB_NAME"
python scripts/apply_schema.py || echo "Schema zaten mevcut"

echo -e "${YELLOW}[8/10] Systemd service yapılandırılıyor...${NC}"
cp efys.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable efys.service

echo -e "${YELLOW}[9/10] Nginx yapılandırılıyor...${NC}"
cp nginx-efys.conf /etc/nginx/sites-available/efys
ln -sf /etc/nginx/sites-available/efys /etc/nginx/sites-enabled/efys
nginx -t && systemctl reload nginx

echo -e "${YELLOW}[10/10] Dosya izinleri ayarlanıyor...${NC}"
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR
chmod 600 $APP_DIR/.env
chown -R www-data:www-data /var/log/$APP_NAME
chown -R www-data:www-data /var/run/$APP_NAME

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ KURULUM TAMAMLANDI!                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Sonraki Adımlar:${NC}"
echo ""
echo -e "1️⃣  .env dosyasını düzenleyin:"
echo -e "   ${YELLOW}nano $APP_DIR/.env${NC}"
echo ""
echo -e "2️⃣  Database URL'yi güncelleyin:"
echo -e "   ${YELLOW}DATABASE_URL=postgresql://$DB_USER:efys_secure_password_2026@localhost:5432/$DB_NAME${NC}"
echo ""
echo -e "3️⃣  SECRET_KEY oluşturun:"
echo -e "   ${YELLOW}python3 -c 'import secrets; print(secrets.token_hex(32))'${NC}"
echo ""
echo -e "4️⃣  Nginx domain ayarlayın:"
echo -e "   ${YELLOW}nano /etc/nginx/sites-available/efys${NC}"
echo -e "   server_name kısmını domain'inizle değiştirin"
echo ""
echo -e "5️⃣  SSL sertifikası alın (Let's Encrypt):"
echo -e "   ${YELLOW}certbot --nginx -d yourdomain.com -d www.yourdomain.com${NC}"
echo ""
echo -e "6️⃣  EFYS servisini başlatın:"
echo -e "   ${YELLOW}systemctl start efys${NC}"
echo -e "   ${YELLOW}systemctl status efys${NC}"
echo ""
echo -e "7️⃣  Log'ları kontrol edin:"
echo -e "   ${YELLOW}tail -f /var/log/efys/error.log${NC}"
echo ""
echo -e "${GREEN}🚀 Uygulama hazır: http://your-server-ip${NC}"
echo ""
