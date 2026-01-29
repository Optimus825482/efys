#!/bin/bash
set -e

echo "🚀 EFYS Docker Container Starting..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=$DB_PASSWORD psql -h postgres -U $DB_USER -d $DB_NAME -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis
echo "⏳ Waiting for Redis..."
until redis-cli -h redis -a $REDIS_PASSWORD ping 2>/dev/null | grep -q PONG; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🗄️ Checking database schema..."
python scripts/apply_schema.py || echo "⚠️  Schema already applied"

# Generate demo data (only if tables are empty)
if [ "$GENERATE_DEMO_DATA" = "true" ]; then
  echo "📊 Generating demo data..."
  python scripts/generate_demo_readings.py || echo "⚠️  Demo data skipped"
fi

echo "✅ EFYS initialization complete!"
echo "🌐 Starting Gunicorn server..."

# Execute the main command
exec "$@"
