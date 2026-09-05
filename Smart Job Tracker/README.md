# AI Job Tracker - Backend API

A secure, production-ready FastAPI backend for tracking internship and job applications with AI-powered suggestions.

## 🚀 Features

- **User Authentication** - Secure JWT-based auth with bcrypt password hashing
- **Application Tracking** - Full CRUD operations for job applications
- **Dashboard Analytics** - Status breakdowns, trends, and follow-up reminders
- **AI Suggestions** - Context-aware next-step recommendations
- **Rate Limiting** - Protection against brute force and abuse
- **Input Validation** - Comprehensive sanitization and validation
- **Database Migrations** - Version-controlled schema management with Alembic
- **Security Headers** - Protection against common web vulnerabilities

## 📋 Requirements

- Python 3.11+
- PostgreSQL (or SQLite for local development)
- pip

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd "Smart Job Tracker"
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
ENVIRONMENT=development
SECRET_KEY=your-secure-secret-key-here
DATABASE_URL=sqlite:///./job_tracker.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Generate a secure SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Run Database Migrations

```bash
python -m alembic upgrade head
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🏗️ Project Structure

```
Smart Job Tracker/
├── app/
│   ├── routers/          # API route handlers
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── applications.py  # Application CRUD
│   │   ├── dashboard.py  # Analytics endpoints
│   │   └── ai.py         # AI suggestion endpoint
│   ├── services/         # Business logic
│   │   └── ai_service.py # AI suggestion engine
│   ├── auth.py           # JWT utilities
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection
│   ├── dependencies.py   # FastAPI dependencies
│   ├── main.py           # Application entrypoint
│   ├── middleware.py     # Rate limiting & security
│   ├── models.py         # SQLAlchemy models
│   └── schemas.py        # Pydantic schemas
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   ├── env.py           # Alembic configuration
│   └── README.md        # Migration documentation
├── .env                  # Environment variables (gitignored)
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔐 Security Features

### Rate Limiting

Built-in protection against abuse:
- **Login:** 5 requests/minute
- **Register:** 3 requests/minute
- **Applications:** 30 requests/minute
- **Dashboard:** 20 requests/minute
- **AI Suggestions:** 10 requests/minute

### Input Validation

All user input is validated and sanitized:
- Field length limits
- URL format validation
- Date range validation
- Whitespace trimming
- Special character restrictions

### Security Headers

All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`

### Authentication

- JWT tokens with configurable expiration
- Bcrypt password hashing
- SECRET_KEY validation in production
- Secure password requirements

## 📊 Database Migrations

### Create a Migration

After modifying models:

```bash
python -m alembic revision --autogenerate -m "Description"
```

### Apply Migrations

```bash
python -m alembic upgrade head
```

### Rollback

```bash
python -m alembic downgrade -1
```

See `alembic/README.md` for detailed migration documentation.

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Register User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Create Application

```bash
curl -X POST http://localhost:8000/applications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Google",
    "role": "Software Engineer",
    "location": "Mountain View, CA",
    "apply_link": "https://careers.google.com",
    "status": "applied",
    "date_applied": "2024-01-15"
  }'
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Generate secure `SECRET_KEY` (32+ chars)
- [ ] Configure production `DATABASE_URL`
- [ ] Set `FRONTEND_URL` for CORS
- [ ] Run migrations: `python -m alembic upgrade head`
- [ ] Use production WSGI server (Gunicorn/Uvicorn workers)
- [ ] Configure reverse proxy (Nginx)
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure database backups

### Production Server

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Environment Variables

```bash
ENVIRONMENT=production
SECRET_KEY=<64-char-hex-string>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=https://your-frontend-domain.com
```

## 📖 Documentation

- **[PHASE_1_IMPROVEMENTS.md](PHASE_1_IMPROVEMENTS.md)** - Security & stability improvements
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Upgrade guide for existing deployments
- **[alembic/README.md](alembic/README.md)** - Database migration documentation

## 🛡️ API Endpoints

### Authentication

- `POST /auth/register` - Create new user
- `POST /auth/login` - Login and get JWT token

### Applications

- `GET /applications` - List all applications (with optional status filter)
- `POST /applications` - Create new application
- `GET /applications/{id}` - Get single application
- `PUT /applications/{id}` - Update application
- `DELETE /applications/{id}` - Delete application

### Dashboard

- `GET /dashboard/summary` - Get analytics and recent data

### AI Suggestions

- `POST /ai/suggest/{application_id}` - Get AI-powered next steps

### Health

- `GET /` - Basic health check
- `GET /health` - Detailed health with database status

## 🔧 Configuration

### Database

**SQLite (Development):**
```bash
DATABASE_URL=sqlite:///./job_tracker.db
```

**PostgreSQL (Production):**
```bash
DATABASE_URL=postgresql://user:password@host:5432/database
```

**Supabase:**
```bash
DATABASE_URL=postgresql://postgres:[password]@[project-ref].supabase.co:5432/postgres
```

### JWT

```bash
SECRET_KEY=<64-char-random-hex>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### CORS

```bash
FRONTEND_URL=https://your-frontend.com
```

Default allowed origins (development):
- http://localhost:5173
- http://localhost:4173
- http://127.0.0.1:5173

## 🐛 Troubleshooting

### "Target database is not up to date"

Run migrations:
```bash
python -m alembic upgrade head
```

### "SECRET_KEY validation error"

In production, SECRET_KEY must be:
- Not the default value
- At least 32 characters long

Generate new one:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### "Rate limit exceeded"

Wait for the rate limit window to expire, or adjust limits in `app/middleware.py`.

### Database connection errors

Check:
1. DATABASE_URL is correct
2. Database server is running
3. Network connectivity
4. Credentials are valid

## 📝 Development

### Adding New Endpoints

1. Create route in `app/routers/`
2. Add schema to `app/schemas.py`
3. Update model if needed in `app/models.py`
4. Create migration: `python -m alembic revision --autogenerate -m "..."`
5. Test endpoint

### Adding New Fields

1. Update model in `app/models.py`
2. Update schema in `app/schemas.py`
3. Create migration: `python -m alembic revision --autogenerate -m "Add field"`
4. Apply: `python -m alembic upgrade head`

## 📜 License

[Your License Here]

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API docs at `/docs`

## 🎯 Roadmap

- [ ] Refresh token implementation
- [ ] Pagination on list endpoints
- [ ] Full-text search
- [ ] Email notifications
- [ ] Export to CSV/PDF
- [ ] Comprehensive test suite
- [ ] API versioning
- [ ] WebSocket for real-time updates
- [ ] Advanced analytics

---

Built with ❤️ using FastAPI
