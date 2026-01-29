#!/bin/bash
# EFYS - GitHub'a Push Script (Linux/Mac)
# Kullanım: ./PUSH_TO_GITHUB.sh

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  EFYS → GitHub Push & Auto-Deploy${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# Git kurulu mu kontrol et
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git bulunamadı! Git kurmanız gerekiyor.${NC}"
    echo -e "${YELLOW}Kurulum: sudo apt install git${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Git kurulu${NC}"

# Repository klasöründe miyiz?
if [ ! -d ".git" ]; then
    echo -e "${CYAN}📁 Git repository başlatılıyor...${NC}"
    git init
    git branch -M main
    echo -e "${GREEN}✅ Git repository başlatıldı${NC}"
fi

# Remote repository kontrolü
REMOTE=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE" ]; then
    echo -e "${CYAN}🔗 Remote repository ekleniyor...${NC}"
    git remote add origin https://github.com/Optimus825482/efys.git
    echo -e "${GREEN}✅ Remote repository eklendi${NC}"
elif [ "$REMOTE" != "https://github.com/Optimus825482/efys.git" ]; then
    echo -e "${YELLOW}⚠️  Remote repository farklı: $REMOTE${NC}"
    echo -e "${CYAN}🔄 Remote repository güncelleniyor...${NC}"
    git remote set-url origin https://github.com/Optimus825482/efys.git
    echo -e "${GREEN}✅ Remote repository güncellendi${NC}"
fi

# Git status
echo ""
echo -e "${CYAN}📊 Değişiklikler:${NC}"
git status --short

# Commit message
echo ""
read -p "💬 Commit mesajı (boş bırakırsanız otomatik oluşturulur): " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    COMMIT_MSG="Update: EFYS - $TIMESTAMP"
fi

# Git add
echo ""
echo -e "${CYAN}📦 Değişiklikler stage'e alınıyor...${NC}"
git add .
echo -e "${GREEN}✅ Tüm değişiklikler eklendi${NC}"

# Git commit
echo ""
echo -e "${CYAN}💾 Commit yapılıyor...${NC}"
if git commit -m "$COMMIT_MSG"; then
    echo -e "${GREEN}✅ Commit başarılı${NC}"
else
    echo -e "${YELLOW}⚠️  Commit oluşturulamadı (değişiklik yok olabilir)${NC}"
fi

# Git push
echo ""
echo -e "${CYAN}🚀 GitHub'a push yapılıyor...${NC}"
echo -e "${CYAN}Repository: https://github.com/Optimus825482/efys.git${NC}"
if git push -u origin main; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  ✅ PUSH BAŞARILI!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo -e "${CYAN}🎯 Sonraki Adımlar:${NC}"
    echo ""
    echo -e "1️⃣  GitHub Actions'ı izleyin:"
    echo -e "   ${YELLOW}https://github.com/Optimus825482/efys/actions${NC}"
    echo ""
    echo -e "2️⃣  Deployment loglarını takip edin"
    echo -e "   ${YELLOW}GitHub → Actions → Latest workflow run${NC}"
    echo ""
    echo -e "3️⃣  Deployment tamamlandığında site kontrolü:"
    echo -e "   ${YELLOW}https://yourdomain.com${NC}"
    echo ""
    echo -e "${CYAN}⏱️  Tahmini deployment süresi: 2-3 dakika${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}  ❌ PUSH BAŞARISIZ!${NC}"
    echo -e "${RED}================================================${NC}"
    echo ""
    echo -e "${YELLOW}🔍 Olası Nedenler:${NC}"
    echo "1. GitHub authentication gerekiyor"
    echo "2. Repository'e yazma izniniz yok"
    echo "3. İnternet bağlantısı yok"
    echo ""
    echo -e "${CYAN}💡 Çözüm:${NC}"
    echo -e "${YELLOW}git config --global user.name 'Your Name'${NC}"
    echo -e "${YELLOW}git config --global user.email 'your.email@example.com'${NC}"
    echo ""
    echo -e "${CYAN}🔐 GitHub Personal Access Token gerekebilir:${NC}"
    echo -e "${YELLOW}https://github.com/settings/tokens${NC}"
    echo ""
    exit 1
fi

echo ""
echo -e "${CYAN}📖 Daha fazla bilgi: GITHUB_DEPLOYMENT_SETUP.md${NC}"
echo ""
