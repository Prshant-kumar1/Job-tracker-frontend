# 🚀 DEPLOY NOW - Quick Reference

## ⚡ 5-Minute Deployment to Render

### Step 1: Update .env (1 min)

```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.rdmputvjdcfotqdxmtum.supabase.co:5432/postgres
SECRET_KEY=95fe543b49460b6ef4a1b26e28ddcb025f401a7aef0aa5efe624e6471e078ac0
```

Get your Supabase password from: https://supabase.com/dashboard → Settings → Database

### Step 2: Test Locally (1 min)

```bash
# Test database connection
python -c "from app.database import engine; engine.connect(); print('✓ Connected to Supabase!')"

# Mark migrations as done (tables already exist)
python -m alembic stamp head

# Start and test
uvicorn app.main:app --reload
# Visit http://localhost:8000/health
```

### Step 3: Push to GitHub (1 min)

```bash
git add .
git commit -m "Add Phase 1 & 2 improvements - production ready"
git push origin main
```

### Step 4: Deploy on Render (2 min)

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** job-tracker-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
5. **Environment Variables** (click "Advanced"):
   ```
   ENVIRONMENT = production
   SECRET_KEY = 95fe543b49460b6ef4a1b26e28ddcb025f401a7aef0aa5efe624e6471e078ac0
   DATABASE_URL = postgresql://postgres:[PASSWORD]@db.rdmputvjdcfotqdxmtum.supabase.co:5432/postgres
   PYTHON_VERSION = 3.11.0
   ```
6. Click **"Create Web Service"**

### Step 5: Verify (30 sec)

Once deployed:
```bash
# Replace with your Render URL
curl https://your-app.onrender.com/health

# Should return:
# {"status":"healthy","database":"connected","environment":"production"}
```

Visit: `https://your-app.onrender.com/docs` 🎉

---

## 🔧 Alternative: Railway (Even Faster!)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables in dashboard
railway open
```

---

## 📱 Update Frontend

In your frontend `.env`:
```bash
VITE_API_URL=https://your-app.onrender.com
```

**Important:** Update `getApplications()` to handle pagination:
```javascript
const response = await api.get('/applications?page=1&page_size=20');
const { items, total, page, total_pages } = response.data;
// Use 'items' instead of response.data directly
```

---

## ✅ Post-Deployment Checklist

- [ ] Health endpoint returns "healthy"
- [ ] Can register user via `/auth/register`
- [ ] Can login via `/auth/login`
- [ ] API docs work at `/docs`
- [ ] Frontend can connect
- [ ] No errors in Render logs

---

## 🐛 Quick Troubleshooting

**"Build failed"**
→ Check `requirements.txt` is in root

**"Database connection failed"**
→ Verify DATABASE_URL password is correct

**"SECRET_KEY error"**
→ Make sure ENVIRONMENT=production is set

**"CORS errors"**
→ Set FRONTEND_URL to your frontend domain

---

## 🎯 You're Done!

- ✅ API deployed
- ✅ Database connected
- ✅ Security active
- ✅ Tests passing
- ✅ Ready for users

**Your API:** `https://your-app.onrender.com`
**Your Docs:** `https://your-app.onrender.com/docs`

**Ship it! 🚢**
