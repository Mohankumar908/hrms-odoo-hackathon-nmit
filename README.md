# Dayflow — Human Resource Management System

Django-based HRMS for the Odoo x NMIT Hackathon.

## Tech Stack
- Python
- Django
- SQLite
- HTML/CSS/JavaScript
- Bootstrap 5 (to be added during UI implementation)

## Team Structure
- Member 1: Backend / Authentication / Employees
- Member 2: Attendance / Leave
- Member 3: Payroll / UI

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Django Apps
- accounts
- employees
- attendance
- leaves
- payroll
