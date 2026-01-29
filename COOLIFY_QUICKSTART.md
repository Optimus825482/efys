# 🚀 EFYS Coolify Quick Start

## ✅ Pre-Deployment Checklist

**Database Status:** ✅ CONNECTED

- Host: 77.42.68.4:5436
- Database: osos_db
- Tables: 24 (17 MB data)
- Health: 100% cache hit rate

**Files Ready:** ✅ ALL PRESENT

- ✅ Dockerfile.coolify
- ✅ .env.coolify
- ✅ app.py (with /health endpoint)
- ✅ gunicorn.conf.py
- ✅ requirements.txt

---

## 🎯 5-Minute Deployment

### Step 1: Create Application in Coolify

1. Login to Coolify Dashboard
2. Click **New Resource** → **Application**
3. Select **Git Repository** or **Public Repository**
4. Enter your repository URL

### Step 2: Configure Build

**Build Pack:** Dockerfile

**Dockerfile Path:** `Dockerfile.coolify`

**Build Context:** `.` (root)

### Step 3: Environment Variables

Copy-paste these into Coolify Environment tab:

```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=CHANGE-THIS-TO-RANDOM-STRING-IN-PRODUCTION
DATABASE_URL=postgresql://postgres:518518Erkan@77.42.68.4:5436/osos_db
APP_NAME=EFYS
APP_VERSION=1.0.0
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
GUNICORN_BIND=0.0.0.0:8000
SESSION_COOKIE_SECURE=true
PERMANENT_SESSION_LIFETIME=86400
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/app/uploads
LOG_LEVEL=INFO
LOG_FILE=/app/logs/efys.log
TZ=Europe/Istanbul
```

**⚠️ IMPORTANT:** Change `SECRET_KEY` to a random string!

Generate one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 4: Port Configuration

**Application Port:** `8000`

**Public Port:** `80` (or `443` for SSL)

### Step 5: Health Check

**Path:** `/health`

**Interval:** 30s

**Timeout:** 10s

**Start Period:** 40s

### Step 6: Persistent Storage

Addontainer Path: `/app/uploads`

- Size: 5GB

**Volume 2 - Logs:**

- Container Path: `/app/logs`
- Size: 1GB

### Step 7: Domain & SSL

**Domain:** `efys.yourdomain.com`

**SSL:** Enable Let's Encrypt (automatic)

### Step 8: Deploy! 🚀

Click **Deploy** button and wait ~2-3 minutes.

---

## 🧪 Post-Deployment Tests

### 1. Health Check

```bash
curl https://efys.yourdomain.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "app": "EFYS",
  "version": "1.0.0",
  "database": "connected"
}
```

### 2. Login Page

```bash
curl https://efys.yourdomain.com/login
```

Should return HTML with login form.

### 3. Static Files

```bash
curl https://efys.yourdomain.com/static/css/efys.css
```

Should return CSS content.

---

## 📊 Monitoring

### Coolify Dashboard

Monitor these metrics:

- **CPU Usage:** Should be < 50%
- **Memory Usage:** Should be < 512MB
- **Response Time:** Should be < 500ms
- **Error Rate:** Should be 0%

### Application Logs

View logs in Coolify:

1. Go to your application
2. Click **Logs** tab
3. Enable **Follow** mode

### Database Monitoring

Check database health:

```bash
# From Coolify container
docker exec -it <container-id> bash
psql postgresql://postgres:518518Erkan@77.42.68.4:5436/osos_db

# Check connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'osos_db';

# Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.'||tablename) DESC;
```

---

## 🔧 Troubleshooting

### Problem: Build Failed

**Solution:**

1. Check Dockerfile path: `Dockerfile.coolify`
2. Verify all files are committed to Git
3. Check build logs in Coolify

### Problem: Health Check Failed

**Solution:**

1. Check if port 8000 is exposed
2. Verify `/health` endpoint exists
3. Check application logs for errors

### Problem: Database Connection Error

**Solution:**

1. Verify DATABASE_URL in environment variables
2. Check if Coolify server can reach 77.42.68.4:5436
3. Test connection from container:

```bash
docker exec -it <container-id> bash
psql postgresql://postgres:518518Erkan@77.42.68.4:5436/osos_db
```

### Problem: Static Files Not Loading

**Solution:**

1. Check if `/app/static` directory exists in container
2. Verify Dockerfile copies static files
3. Check Nginx/Coolify reverse proxy config

### Problem: File Upload Not Working

**Solution:**

1. Verify `/app/uploads` volume is mounted
2. Check write permissions
3. Verify MAX_CONTENT_LENGTH setting

---

## 🔄 Update Deployment

To update your application:

1. Push changes to Git repository
2. Go to Coolify Dashboard
3. Click **Redeploy** button
4. Wait for build to complete
5. Health check will verify deployment

---

## 📈 Performance Optimization

### 1. Increase Workers

If CPU usage is low but response time is high:

```env
GUNICORN_WORKERS=8  # Increase from 4
```

### 2. Add Redis Cache

For session storage and caching:

1. Add Redis service in Coolify
2. Update environment:

```env
REDIS_URL=redis://:<password>@redis:6379/0
```

### 3. Enable Gzip Compression

Coolify's reverse proxy should handle this automatically.

### 4. CDN for Static Files

For better performance, serve static files from CDN:

- Upload `/static` to CDN
- Update templates to use CDN URLs

---

## 🔐 Security Checklist

- [x] Database connection uses external PostgreSQL (not exposed)
- [x] SECRET_KEY is unique and strong
- [x] SESSION_COOKIE_SECURE=true (HTTPS only)
- [x] Application runs as non-root user (efys)
- [x] Health check endpoint doesn't expose sensitive data
- [ ] Firewall rules configured (allow only Coolify IP to DB)
- [ ] SSL certificate active (Let's Encrypt)
- [ ] Regular backups configured
- [ ] Monitoring and alerts set up

---

## 📞 Support

### Coolify Issues

- Check Coolify logs
- Verify environment variables
- Test health check endpoint

### Application Issues

- Check application logs: `/app/logs/efys.log`
- Verify database connection
- Test endpoints manually

### Database Issues

- Check PostgreSQL logs
- Verify connection from Coolify server
- Monitor active connections

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ Health check returns 200 OK
✅ Login page loads correctly
✅ Static files load (CSS, JS)
✅ Database queries work
✅ File uploads work
✅ Logs are being written
✅ SSL certificate is active
✅ Response time < 500ms

---

## 📝 Next Steps

After successful deployment:

1. **Configure Backups**
   - Database: Daily backups
   - Uploads: Weekly backups

2. **Set Up Monitoring**
   - Uptime monitoring (UptimeRobot, Pingdom)
   - Error tracking (Sentry)
   - Performance monitoring (New Relic, DataDog)

3. **Configure Alerts**
   - Health check failures
   - High CPU/Memory usage
   - Database connection errors
   - Disk space warnings

4. **Documentation**
   - User manual
   - API documentation
   - Deployment runbook

---

**Deployment başarılı olsun! 🚀**

Need help? Check `COOLIFY_DEPLOYMENT.md` for detailed guide.
two volumes:

**Volume 1 - Uploads:**

- C
