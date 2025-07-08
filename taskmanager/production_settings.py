from .settings import *
import os

# Override settings for production
DEBUG = False

# Security settings
ALLOWED_HOSTS = [
    '167.71.32.251',  # Replace with your actual IP
    'localhost',
    '127.0.0.1',
]

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'task_manager_db'),
        'USER': os.environ.get('DB_USER', 'task_manager_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = False  # Set to True when you have SSL
SECURE_HSTS_SECONDS = 0  # Set to 31536000 when you have SSL
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # Set to True when you have SSL
SECURE_HSTS_PRELOAD = False  # Set to True when you have SSL

# Session security
SESSION_COOKIE_SECURE = False  # Set to True when you have SSL
CSRF_COOKIE_SECURE = False  # Set to True when you have SSL

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/deploy/task_manager/django_errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
