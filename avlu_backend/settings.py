"""
Django settings for avlu_backend project.
Tam uyumlu nihai sürüm.
"""

from pathlib import Path
import os
import environ # django-environ kütüphanesi

# 1. Env başlatma
env = environ.Env(
    # Varsayılan değerler (Hata almamak için)
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'django-insecure-local-key'),
    DATABASE_URL=(str, 'sqlite:///db.sqlite3')
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env dosyasını oku (Varsa)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# --- GÜVENLİK AYARLARI ---
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['https://*.run.app'])

# --- UYGULAMALAR ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # <--- Eklendi
    'django.contrib.staticfiles',
    'core',  # Senin uygulaman
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- EN ÖNEMLİSİ (CSS İçin)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'avlu_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Gerekirse os.path.join(BASE_DIR, 'templates') eklenebilir
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'avlu_backend.wsgi.application'

# --- VERİTABANI ---
# Localde SQLite, Cloud'da PostgreSQL kullanır.
DATABASES = {
    'default': env.db()
}

# --- ŞİFRE DOĞRULAMA ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- DİL VE SAAT ---
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# --- STATİK DOSYALAR (CSS/JS) ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- GİRİŞ/ÇIKIŞ AYARLARI ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'ana_sayfa' # Veya gitmek istediğin sayfa
LOGOUT_REDIRECT_URL = 'login'

# --- EMAIL (OPSİYONEL) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD', default='')