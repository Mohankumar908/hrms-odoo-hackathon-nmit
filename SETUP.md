# DAYFLOW Setup — Run These Commands

## Step 1: Install dependencies
```
pip install django==5.0.6 djangorestframework==3.15.2 djangorestframework-simplejwt==5.3.1 django-cors-headers==4.4.0 psycopg2-binary==2.9.9 python-decouple==3.8 Pillow==10.3.0 django-filter==24.3 drf-spectacular==0.27.2 whitenoise==6.7.0 gunicorn==22.0.0 openpyxl==3.1.5
```

## Step 2: Migrate
```
python manage.py migrate
```

## Step 3: Seed data
```
python manage.py seed_data
```

## Step 4: Create admin user
```
python manage.py createsuperuser
```

## Step 5: Run
```
python manage.py runserver
```

## Login
Go to: http://127.0.0.1:8000/accounts/login/

## API Docs
http://127.0.0.1:8000/api/docs/
