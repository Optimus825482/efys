#!/bin/bash
# EFYS Database & Files Backup Script
# Kullanım: ./backup.sh
# Cron: 0 2 * * * /var/www/efys/backup.sh (her gece 02:00)

set -e

# Configuration
APP_DIR="/var/www/efys"
BACKUP_DIR="/var/backups/efys"
DB_NAME="efys_production"
DB_USER="efys_user"
DB_PASSWORD="efys_secure_password_2026"
RETENTION_DAYS=30

# Date format
DATE=$(date +"%Y%m%d_%H%M%S")
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create backup directory
mkdir -p $BACKUP_DIR/database
mkdir -p $BACKUP_DIR/uploads
mkdir -p $BACKUP_DIR/logs

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  EFYS Backup - $TIMESTAMP${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

# 1. Database Backup
echo -e "${GREEN}[1/3] Database yedekleniyor...${NC}"
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > "$BACKUP_DIR/database/${DB_NAME}_${DATE}.sql.gz"
echo "✅ Database: ${DB_NAME}_${DATE}.sql.gz"

# 2. Uploads Backup
echo -e "${GREEN}[2/3] Yüklenen dosyalar yedekleniyor...${NC}"
if [ -d "$APP_DIR/uploads" ] && [ "$(ls -A $APP_DIR/uploads)" ]; then
    tar -czf "$BACKUP_DIR/uploads/uploads_${DATE}.tar.gz" -C $APP_DIR uploads
    echo "✅ Uploads: uploads_${DATE}.tar.gz"
else
    echo "⚠️  Uploads klasörü boş"
fi

# 3. Logs Backup
echo -e "${GREEN}[3/3] Log dosyaları yedekleniyor...${NC}"
if [ -d "/var/log/efys" ] && [ "$(ls -A /var/log/efys)" ]; then
    tar -czf "$BACKUP_DIR/logs/logs_${DATE}.tar.gz" -C /var/log efys
    echo "✅ Logs: logs_${DATE}.tar.gz"
else
    echo "⚠️  Logs klasörü boş"
fi

# 4. Cleanup old backups (30 günden eski)
echo -e "${GREEN}Eski yedekler temizleniyor (${RETENTION_DAYS} günden eski)...${NC}"
find $BACKUP_DIR/database -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/uploads -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/logs -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# 5. Backup size report
DB_SIZE=$(du -sh $BACKUP_DIR/database | cut -f1)
UPLOADS_SIZE=$(du -sh $BACKUP_DIR/uploads | cut -f1)
LOGS_SIZE=$(du -sh $BACKUP_DIR/logs | cut -f1)
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Backup tamamlandı!${NC}"
echo ""
echo "📦 Database: $DB_SIZE"
echo "📦 Uploads:  $UPLOADS_SIZE"
echo "📦 Logs:     $LOGS_SIZE"
echo "📦 Toplam:   $TOTAL_SIZE"
echo ""
echo "📂 Konum: $BACKUP_DIR"
echo -e "${BLUE}════════════════════════════════════════${NC}"

# Optional: Remote backup (rsync to backup server)
# rsync -avz --delete $BACKUP_DIR/ backup-server:/backup/efys/

exit 0
