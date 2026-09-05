# 🚀 Quick Start Guide

Get your AI Job Tracker backend running in 5 minutes.

## Prerequisites

- Python 3.11+
- pip
- Git

## Step 1: Install Dependencies (1 min)

```bash
cd "Smart Job Tracker"
pip install -r requirements.txt
```

## Step 2: Configure Environment (1 min)

```bash
# Copy example environment file
cp .env.example .env
```

Your `.env` already has a secure SECRET_KEY. For local development, you're good to go!

**Current configuration:**
```bash
ENVIRONMENT=development
SECRET_KEY=95fe543b49460b6ef4a1b26e28ddcb025f401a7aef0aa5efe624e6471e078ac0
DATABASE_URL=sqlite:///./job_tracker.db
```

## Step 3: Setup Database (1 min)

```bash
# Run migrations to create tables
python -m alembic upgrade head
```

You should see:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 28152dc0c7fc, Initial migration
```

## Step 4: Start Server (1 min)

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## Step 5: Test It! (1 min)

### Open API Docs

Visit http://localhost:8000/docs in your browser.

You'll see interactive API documentation where you can test all endpoints!

### Or use curl

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "environment": "development",
  "frontend_url_configured": false
}
```

## 🎉 You're Running!

Your backend is now running with:
- ✅ Secure authentication
- ✅ Rate limiting
- ✅ Input validation
- ✅ Database migrations
- ✅ Security headers

## 🧪 Try These Commands

### Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Copy the `access_token` from the response.

### Create Application

```bash
curl -X POST http://localhost:8000/applications \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Google",
    "role": "Software Engineer",
    "status": "applied",
    "date_applied": "2024-01-15"
  }'
```

### Get Dashboard

```bash
curl http://localhost:8000/dashboard/summary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## 🎯 Next Steps

### Option 1: Connect Frontend

If you have the React frontend:

1. Update frontend `.env`:
   ```bash
   VITE_API_URL=http://localhost:8000
   ```

2. Start frontend:
   ```bash
   cd ../job-tracker-frontend
   npm run dev
   ```

3. Visit http://localhost:5173

### Option 2: Explore API

Visit http://localhost:8000/docs and try all the endpoints:
- Register and login
- Create applications
- View dashboard
- Get AI suggestions
- Update application status

### Option 3: Review Documentation

- `README.md` - Full documentation
- `PHASE_1_IMPROVEMENTS.md` - What was improved
- `alembic/README.md` - Database migrations

## 🔧 Common Issues

### "Command not found: uvicorn"

```bash
# Make sure you installed dependencies
pip install -r requirements.txt

# Or install uvicorn directly
pip install uvicorn[standard]
```

### "ModuleNotFoundError: No module named 'app'"

```bash
# Make sure you're in the right directory
cd "Smart Job Tracker"

# Check you see app/ folder
ls app/
```

### Database errors

```bash
# Reset database
rm job_tracker.db
python -m alembic upgrade head
```

### Port already in use

```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

## 📊 What's Enabled?

### Security Features Active

- ✅ JWT authentication
- ✅ Rate limiting (5 login attempts/min)
- ✅ Input validation
- ✅ Security headers
- ✅ Password hashing (bcrypt)

### Rate Limits

- Login: 5/min
- Register: 3/min
- Applications: 30/min
- Dashboard: 20/min
- AI: 10/min

### Input Validation

All fields are validated:
- ✅ Email format
- ✅ URL format
- ✅ Date ranges
- ✅ Text sanitization
- ✅ Length limits

## 💡 Pro Tips

### Watch Logs

The server shows detailed logs of all requests and errors.

### Auto-Reload

Changes to Python files automatically restart the server (with `--reload` flag).

### Interactive Docs

The `/docs` endpoint lets you test APIs without writing curl commands!

### Database Browsing

For SQLite:
```bash
# Install DB Browser for SQLite
# Open job_tracker.db to see your data
```

## 🎓 Learn More

- **API Docs:** http://localhost:8000/docs
- **Full README:** [README.md](README.md)
- **Security Features:** [PHASE_1_IMPROVEMENTS.md](PHASE_1_IMPROVEMENTS.md)
- **Migrations:** [alembic/README.md](alembic/README.md)

## 🚀 Ready for Production?

See deployment checklist in [README.md](README.md#-deployment)

Key steps:
1. Set `ENVIRONMENT=production`
2. Use PostgreSQL (not SQLite)
3. Set secure SECRET_KEY
4. Configure FRONTEND_URL
5. Use production WSGI server

---

**Enjoy your secure, production-ready API!** 🎉

Need help? Check the documentation or create an issue.
