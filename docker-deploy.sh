#!/bin/bash
# EFYS Docker Quick Deploy Script for Coofy Server
# Usage: curl -sSL https://raw.githubusercontent.com/Optimus825482/efys/main/docker-deploy.sh | bash

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  EFYS Docker Deployment - Coofy Server        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Bu script root olarak çalıştırılmalı${NC}"
    echo "Kullanım: sudo bash docker-deploy.sh"
    exit 1
fi

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}[1/6] Docker kuruluyor...${NC}"
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✅ Docker kuruldu${NC}"
else
    echo -e "${GREEN}✅ Docker zaten kurulu${NC}"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}[2/6] Docker Compose kuruluyor...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose kuruldu${NC}"
else
    echo -e "${GREEN}✅ Docker Compose zaten kurulu${NC}"
fi

# Create app directory
echo -e "${YELLOW}[3/6] Uygulama dizini oluşturuluyor...${NC}"
mkdir -p /opt/efys
cd /opt/efys

# Clone or update repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}[4/6] Repository güncelleniyor...${NC}"
    git pull origin main
else
    echo -e "${YELLOW}[4/6] Repository clone ediliyor...${NC}"
    git clone https://github.com/Optimus825482/efys.git .
fi

# Create necessary directories
mkdir -p uploads logs docker/ssl

# Setup environment file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[5/6] Environment dosyası oluşturuluyor...${NC}"
    cp .env.docker.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-super-secret-key-change-this-32-chars-minimum/$SECRET_KEY/" .env
    
    # Generate strong passwords
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
    
    sed -i "s/efys_secure_password_2026_change_this/$DB_PASSWORD/" .env
    sed -i "s/redis_secure_password_change_this/$REDIS_PASSWORD/" .env
    
    echo -e "${GREEN}✅ Environment dosyası oluşturuldu${NC}"
    echo -e "${YELLOW}⚠️  .env dosyasını kontrol edin ve domain ayarlarını yapın${NC}"
else
    echo -e "${GREEN}✅ Environment dosyası mevcut${NC}"
fi

# Build and start containers
echo -e "${YELLOW}[6/6] Docker containers başlatılıyor...${NC}"
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo -e "${BLUE}⏳ Servisler başlatılıyor...${NC}"
sleep 10

# Check container status
docker-compose ps

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ KURULUM TAMAMLANDI!                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Container Status:${NC}"
docker-compose ps
echo ""
echo -e "${BLUE}🌐 EFYS şu adreste çalışıyor:${NC}"
echo -e "   ${YELLOW}http://$(hostname -I | awk '{print $1}')${NC}"
echo ""
echo -e "${BLUE}🔍 Yararlı Komutlar:${NC}"
echo -e "   ${YELLOW}docker-compose logs -f app${NC}     # Uygulama logları"
echo -e "   ${YELLOW}docker-compose ps${NC}              # Container durumu"
echo -e "   ${YELLOW}docker-compose restart${NC}         # Yeniden başlat"
echo -e "   ${YELLOW}docker-compose down${NC}            # Durdur"
echo ""
echo -e "${BLUE}📝 Sonraki Adımlar:${NC}"
echo "1. .env dosyasını düzenleyin: nano /opt/efys/.env"
echo "2. Domain ayarlarını yapın: nano /opt/efys/docker/nginx.conf"
echo "3. SSL sertifikası ekleyin (Let's Encrypt veya manuel)"
echo "4. Container'ları yeniden başlatın: docker-compose restart"
echo ""
