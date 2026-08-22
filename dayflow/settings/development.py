"""
DAYFLOW HRMS - Development Settings
"""
from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CORS_ALLOW_ALL_ORIGINS = True

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Debug toolbar disabled
