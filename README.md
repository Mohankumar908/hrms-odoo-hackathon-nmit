# DAYFLOW HRMS
> Every workday, perfectly aligned.

## Quick Start (Local Dev)

```bash
# 1. Clone & setup
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY, DB settings, etc.

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Run
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Docker
```bash
docker-compose up --build
```

## API Docs
- Swagger: http://localhost:8000/api/docs/
- ReDoc:   http://localhost:8000/api/redoc/

## Key URLs
| URL | Description |
|-----|-------------|
| `/accounts/login/` | Login |
| `/` | Dashboard (role-based redirect) |
| `/employees/list/` | Employee list (HR/Admin) |
| `/attendance/` | Attendance |
| `/leave/` | Leave management |
| `/payroll/` | Payroll |
| `/projects/` | Projects |
| `/tasks/` | Tasks |
| `/work-updates/` | Daily work updates |
| `/analytics/` | Analytics & AI insights |
| `/reports/` | Reports & exports |
| `/admin/` | Django admin |

## Roles
- **Admin** — Full access
- **HR** — People & reports
- **Employee** — Own data only
