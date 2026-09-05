# Supabase Deployment Guide

Complete guide to deploying your Job Tracker API to Supabase.

## 🎯 Overview

Your Supabase project is already set up with:
- PostgreSQL database
- Tables: `users` and `job_applications`
- Project URL: https://rdmputvjdcfotqdxmtum.supabase.co

## 📋 Pre-Deployment Checklist

- [ ] Supabase project created (✅ Done)
- [ ] Database tables exist (✅ Done)
- [ ] Local testing complete
- [ ] Environment variables configured
- [ ] Database migrations ready

## 🔧 Step 1: Update Local .env for Supabase

Update your `.env` file:

```bash
# Environment
ENVIRONMENT=production

# Security
SECRET_KEY=95fe543b49460b6ef4a1b26e28ddcb025f401a7aef0aa5efe624e6471e078ac0

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[YOUR_DB_PASSWORD]@db.rdmputvjdcfotqdxmtum.supabase.co:5432/postgres

# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Frontend CORS (update with your frontend URL)
FRONTEND_URL=https://your-frontend.onrender.com
```

**Get your Supabase DB Password:**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Settings → Database → Connection String
4. Copy the password from the connection string

## 🗄️ Step 2: Apply Database Migrations

Since you already have tables in Supabase, mark them as migrated:

```bash
# Test connection first
python -c "from app.database import engine; from sqlalchemy import text; conn = engine.connect(); print('✓ Connected to Supabase')"

# Mark current state as migrated (don't run migrations, tables exist)
python -m alembic stamp head
```

**Alternative:** If you want a clean start:

```bash
# This will create tables from scratch
python -m alembic upgrade head
```

## 🧪 Step 3: Test Locally with Supabase

Start your server and test with Supabase database:

```bash
# Start server
uvicorn app.main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Should show:
# {
#   "status": "healthy",
#   "database": "connected",
#   "environment": "production"
# }
```

### Test Full Flow:

```bash
# 1. Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpass123"
  }'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
# Save the access_token from response

# 3. Create application
curl -X POST http://localhost:8000/applications \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Google",
    "role": "Software Engineer",
    "status": "applied"
  }'

# 4. Get applications (with pagination)
curl http://localhost:8000/applications?page=1&page_size=20 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🚀 Step 4: Choose Deployment Platform

You have several options for deploying the FastAPI backend:

### Option A: Render (Recommended - Free Tier)

1. **Create `render.yaml`:**

Already in your project root:

```yaml
services:
  - type: web
    name: job-tracker-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: SECRET_KEY
        sync: false  # Set in Render dashboard
      - key: DATABASE_URL
        sync: false  # Set in Render dashboard
      - key: FRONTEND_URL
        sync: false
      - key: PYTHON_VERSION
        value: 3.11.0
```

2. **Add Gunicorn to requirements.txt:**

```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

3. **Deploy to Render:**
   - Go to https://render.com
   - Connect GitHub repository
   - Create new Web Service
   - Select your repository
   - Set environment variables in dashboard:
     - `SECRET_KEY`: your secure key
     - `DATABASE_URL`: Supabase connection string
     - `FRONTEND_URL`: your frontend URL
   - Deploy!

### Option B: Railway (Easy, Paid)

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Initialize and deploy:
```bash
railway login
railway init
railway up
```

3. Set environment variables in Railway dashboard

### Option C: Fly.io (Good for production)

1. Install Fly CLI
2. Create `fly.toml`
3. Deploy with `fly deploy`

### Option D: DigitalOcean App Platform

1. Connect GitHub
2. Configure app
3. Set environment variables
4. Deploy

## 🔐 Step 5: Configure Environment Variables

On your chosen platform, set these environment variables:

```bash
ENVIRONMENT=production
SECRET_KEY=95fe543b49460b6ef4a1b26e28ddcb025f401a7aef0aa5efe624e6471e078ac0
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.rdmputvjdcfotqdxmtum.supabase.co:5432/postgres
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
FRONTEND_URL=https://your-frontend-url.com
```

**⚠️ Security Notes:**
- Never commit `.env` to Git
- Use platform's secret management
- Rotate SECRET_KEY periodically

## ✅ Step 6: Verify Deployment

After deployment, test your live API:

```bash
# Replace with your deployed URL
API_URL="https://your-app.onrender.com"

# Health check
curl $API_URL/health

# Register
curl -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production User",
    "email": "user@example.com",
    "password": "securepass123"
  }'

# Check Swagger docs
open $API_URL/docs
```

## 🔄 Step 7: Update Frontend

Update your frontend to use the deployed API:

**Frontend `.env`:**
```bash
VITE_API_URL=https://your-api.onrender.com
```

**Or in Render/Vercel:**
Set environment variable: `VITE_API_URL=https://your-api.onrender.com`

## 📊 Step 8: Monitor Your Deployment

### Check Logs

**Render:**
```bash
# View in dashboard or
render logs -s job-tracker-api
```

**Railway:**
```bash
railway logs
```

### Monitor Database

**Supabase Dashboard:**
1. Go to Database → Logs
2. Check for errors
3. Monitor query performance

### API Health

Set up monitoring:
- Uptime Robot: https://uptimerobot.com
- Pingdom: https://pingdom.com
- Or use your platform's built-in monitoring

## 🐛 Troubleshooting

### "Database connection failed"

Check:
1. DATABASE_URL is correct
2. Password doesn't have special characters (or URL-encode them)
3. Supabase project is active
4. Network/firewall allows connections

Test connection:
```python
python -c "from app.database import engine; from sqlalchemy import text; conn = engine.connect(); result = conn.execute(text('SELECT 1')); print('✓ Connected')"
```

### "SECRET_KEY validation error"

Make sure:
1. SECRET_KEY is set in environment
2. It's at least 32 characters
3. ENVIRONMENT=production is set

### "Rate limit too aggressive"

Adjust in `app/middleware.py`:
```python
RATE_LIMITS = {
    "/auth/login": (10, 60),      # Increase from 5 to 10
    "/auth/register": (5, 60),     # Increase from 3 to 5
    ...
}
```

### "CORS errors"

1. Make sure FRONTEND_URL is set
2. Check it matches your frontend exactly (no trailing slash)
3. Check browser console for actual error

## 🔒 Security Checklist

- [ ] SECRET_KEY is secure (32+ characters)
- [ ] DATABASE_URL uses SSL (Supabase does by default)
- [ ] ENVIRONMENT=production
- [ ] Rate limiting is active
- [ ] CORS is configured correctly
- [ ] No secrets in Git
- [ ] HTTPS is enabled (automatic on Render/Railway)

## 📈 Performance Optimization

### Database

1. **Add indexes** (if needed):
```sql
CREATE INDEX idx_applications_user_status ON job_applications(user_id, status);
CREATE INDEX idx_applications_user_created ON job_applications(user_id, created_at DESC);
```

2. **Connection pooling** (Render/Railway handle this)

### API

1. **Use more workers**:
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

2. **Add caching** (future enhancement)

## 🎯 Post-Deployment

### 1. Test Everything

- [ ] User registration
- [ ] Login and refresh token
- [ ] Create application
- [ ] List applications (pagination)
- [ ] Update application
- [ ] Delete application
- [ ] Dashboard summary
- [ ] AI suggestions

### 2. Set Up Monitoring

- [ ] Health check pings
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Database monitoring

### 3. Update Documentation

- [ ] Update README with prod URL
- [ ] Document any environment-specific quirks
- [ ] Update frontend README

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ Health endpoint returns "healthy"
- ✅ Can register and login
- ✅ Can create and list applications
- ✅ Rate limiting works
- ✅ Refresh tokens work
- ✅ No errors in logs
- ✅ Frontend connects successfully

## 📞 Support

If you encounter issues:

1. Check logs first
2. Test database connection
3. Verify environment variables
4. Check Supabase status
5. Review platform-specific docs

## 🚀 You're Live!

Once deployed:
- Backend API: `https://your-api.onrender.com`
- API Docs: `https://your-api.onrender.com/docs`
- Frontend: `https://your-frontend.vercel.app`

Share your job tracker with the world! 🎊

---

**Need help?** Check:
- Render docs: https://render.com/docs
- Supabase docs: https://supabase.com/docs
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/
