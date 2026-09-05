# Migration Guide - Upgrading to Phase 1 Improvements

## For Existing Deployments

If you already have the application running with data, follow these steps carefully.

## ⚠️ IMPORTANT: Backup First

```bash
# If using PostgreSQL/Supabase
pg_dump your_database > backup_$(date +%Y%m%d).sql

# If using SQLite
cp job_tracker.db job_tracker_backup_$(date +%Y%m%d).db
```

## Step-by-Step Upgrade

### 1. Pull Latest Code

```bash
git pull origin main
```

### 2. Update Dependencies

```bash
pip install -r requirements.txt
```

This will install Alembic and any other new dependencies.

### 3. Update Environment Configuration

Update your `.env` file:

```bash
# Add this line
ENVIRONMENT=production

# Verify your SECRET_KEY is secure (not the default)
# If it's the default, generate a new one:
python -c "import secrets; print(secrets.token_hex(32))"
```

**⚠️ CRITICAL:** If you change SECRET_KEY, all existing JWT tokens will be invalidated and users will need to log in again.

### 4. Initialize Alembic (First Time Only)

If this is your first time using migrations:

```bash
# Mark current database state as migrated
python -m alembic stamp head
```

This tells Alembic that your database is already at the "latest" version without running any migrations.

### 5. Verify Configuration

```bash
# Test that config loads without errors
python -c "from app.config import settings; print('Config OK')"

# Test database connection
python -c "from app.database import engine; from sqlalchemy import text; conn = engine.connect(); conn.execute(text('SELECT 1')); print('Database OK')"
```

### 6. Test the Application Locally

```bash
# Start the server
uvicorn app.main:app --reload

# In another terminal, test health endpoint
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "development",
  "frontend_url_configured": false
}
```

### 7. Test Rate Limiting

```bash
# Try hitting login endpoint multiple times rapidly
for i in {1..7}; do 
  echo "Request $i"
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}'
  echo ""
done
```

You should see HTTP 429 (Too Many Requests) after the 5th request.

### 8. Test Input Validation

```bash
# Try creating an application with invalid data (requires valid auth token)
curl -X POST http://localhost:8000/applications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "   ",
    "role": "Engineer",
    "apply_link": "not-a-url"
  }'
```

Should return validation errors, not 500 errors.

### 9. Deploy to Production

Once local testing passes:

```bash
# 1. Set production environment variables
export ENVIRONMENT=production
export SECRET_KEY=your-secure-secret-key
export DATABASE_URL=postgresql://...

# 2. Run any pending migrations
python -m alembic upgrade head

# 3. Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## For New Deployments

If you're deploying for the first time:

### 1. Set Environment Variables

```bash
ENVIRONMENT=production
SECRET_KEY=<generate-with-secrets.token_hex(32)>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
FRONTEND_URL=https://your-frontend.com
```

### 2. Run Migrations

```bash
python -m alembic upgrade head
```

This will create all tables.

### 3. Start Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Rollback Plan

If something goes wrong:

### 1. Stop the Application

```bash
# Kill the uvicorn process
pkill -f uvicorn
```

### 2. Restore from Backup

```bash
# PostgreSQL
psql your_database < backup_YYYYMMDD.sql

# SQLite
cp job_tracker_backup_YYYYMMDD.db job_tracker.db
```

### 3. Revert Code

```bash
git checkout <previous-commit-hash>
pip install -r requirements.txt
```

### 4. Restart Old Version

```bash
uvicorn app.main:app --reload
```

## Common Issues

### Issue: "Can't validate SECRET_KEY in production"

**Solution:** Make sure SECRET_KEY is set and is not the default value.

```bash
# Generate new key
python -c "import secrets; print(secrets.token_hex(32))"

# Set in environment
export SECRET_KEY=<generated-key>
```

### Issue: "Target database is not up to date"

**Solution:** Run migrations.

```bash
python -m alembic upgrade head
```

### Issue: "Rate limiting not working"

**Check:**
1. Middleware is properly added in main.py
2. Server is actually restarting (not using cached code)
3. Test from same IP address

### Issue: "Validation errors on existing data"

**Cause:** Old data might not meet new validation rules (e.g., URLs without http://)

**Solution:** Either:
1. Clean up data manually in database
2. Create a data migration to fix invalid records
3. Temporarily relax validation rules for existing data

## Verification Checklist

After deployment, verify:

- [ ] Application starts without errors
- [ ] Health endpoint returns "healthy" status
- [ ] Can register a new user
- [ ] Can log in
- [ ] Can create an application
- [ ] Can view dashboard
- [ ] Rate limiting works (test by hitting login 10 times)
- [ ] Invalid input returns 422, not 500
- [ ] Logs show proper structure
- [ ] Security headers present in responses

## Testing Security Headers

```bash
curl -I http://localhost:8000/
```

Should see headers like:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Monitoring

After deployment, monitor:

1. **Error logs** - Any unhandled exceptions
2. **Rate limit hits** - Legitimate users being blocked?
3. **Validation errors** - Users hitting new validation rules?
4. **Database connections** - Pool exhaustion?

## Support

If you encounter issues not covered here:

1. Check `PHASE_1_IMPROVEMENTS.md` for detailed changes
2. Check `alembic/README.md` for migration help
3. Review error logs: `tail -f logs/app.log`
4. Test health endpoint: `curl http://localhost:8000/health`

## Success Criteria

Your migration is successful when:
- ✅ Application starts and runs
- ✅ All existing functionality works
- ✅ New validations are active
- ✅ Rate limiting is working
- ✅ No data loss
- ✅ Security headers present
- ✅ Error handling improved

Good luck with your deployment! 🚀
