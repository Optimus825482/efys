#!/bin/bash

# EFYS Coolify Setup Script
# Bu script Coolify deployment için gerekli kontrolleri yapar

set -e

echo "=========================================="
echo "EFYS Coolify Deployment Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database connection details
DB_HOST="77.42.68.4"
DB_PORT="5436"
DB_NAME="osos_db"
DB_USER="postgres"
DB_PASS="518518Erkan"

# Check database connection
echo -e "${YELLOW}1. Checking database connection...${NC}"
if PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    echo "Please check your database credentials and network connectivity"
    exit 1
fi

# Check required files
echo -e "${YELLOW}2. Checking required files...${NC}"
REQUIRED_FILES=(
    "app.py"
    "config.py"
    "gunicorn.conf.py"
    "requirements.txt"
    "Dockerfile.coolify"
    ".env.coolify"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file not found${NC}"
        exit 1
    fi
done

# Check required directories
echo -e "${YELLOW}3. Checking required directories...${NC}"
REQUIRED_DIRS=(
    "routes"
    "services"
    "templates"
    "static"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir/${NC}"
    else
        echo -e "${RED}❌ $dir/ not found${NC}"
        exit 1
    fi
done

# Check database tables
echo -e "${YELLOW}4. Checking database tables...${NC}"
TABLE_COUNT=$(PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'")
echo -e "${GREEN}✅ Found $TABLE_COUNT tables${NC}"

if [ "$TABLE_COUNT" -lt 20 ]; then
    echo -e "${YELLOW}⚠️  Warning: Expected at least 20 tables, found $TABLE_COUNT${NC}"
fi

# Generate deployment summary
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo ""
echo "Database:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  Tables: $TABLE_COUNT"
echo ""
echo "Application:"
echo "  Framework: Flask"
echo "  WSGI Server: Gunicorn"
echo "  Port: 8000"
echo "  Health Check: /health"
echo ""
echo "Coolify Configuration:"
echo "  Dockerfile: Dockerfile.coolify"
echo "  Environment: .env.coolify"
echo "  Build Pack: Dockerfile"
echo ""

# Next steps
echo "=========================================="
echo "Next Steps for Coolify Deployment"
echo "=========================================="
echo ""
echo "1. Create new application in Coolify"
echo "2. Select 'Dockerfile' as build pack"
echo "3. Set Dockerfile path to: Dockerfile.coolify"
echo "4. Copy environment variables from .env.coolify"
echo "5. Set application port to: 8000"
echo "6. Configure health check: /health"
echo "7. Add persistent volumes:"
echo "   - /app/uploads (5GB)"
echo "   - /app/logs (1GB)"
echo "8. Deploy!"
echo ""
echo -e "${GREEN}✅ All checks passed! Ready for Coolify deployment${NC}"
echo ""
