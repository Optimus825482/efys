#!/bin/bash
# EFYS Docker Backup Script
# Usage: ./docker-backup.sh

set -e

BACKUP_DIR="/var/backups/efys-docker"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 EFYS Docker Backup başlatılıyor..."

# Create backup directory
mkdir -p $BACKUP_DIR

# 1. Database Backup
echo "📦 [1/3] PostgreSQL backup alınıyor..."
docker-compose exec -T postgres pg_dump -U efys_user efys_production | gzip > "$BACKUP_DIR/database_${TIMESTAMP}.sql.gz"
echo "✅ Database backup: database_${TIMESTAMP}.sql.gz"

# 2. Uploads Backup
echo "📦 [2/3] Uploads backup alınıyor..."
if [ -d "uploads" ] && [ "$(ls -A uploads)" ]; then
    tar -czf "$BACKUP_DIR/uploads_${TIMESTAMP}.tar.gz" uploads/
    echo "✅ Uploads backup: uploads_${TIMESTAMP}.tar.gz"
else
    echo "⚠️  Uploads klasörü boş"
fi

# 3. Environment & Config Backup
echo "📦 [3/3] Config backup alınıyor..."
tar -czf "$BACKUP_DIR/config_${TIMESTAMP}.tar.gz" .env docker-compose.yml docker/
echo "✅ Config backup: config_${TIMESTAMP}.tar.gz"

# Cleanup old backups (30 days)
echo "🧹 Eski backuplar temizleniyor (30 günden eski)..."
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Summary
echo ""
echo "✅ Backup tamamlandı!"
echo "📂 Konum: $BACKUP_DIR"
ls -lh $BACKUP_DIR/*${TIMESTAMP}*
echo ""
