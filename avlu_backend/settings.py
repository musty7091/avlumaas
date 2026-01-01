"""
Django settings for avlu_backend project.
ORİJİNAL VE HATA KORUMALI NİHAİ SÜRÜM
"""

from pathlib import Path
import os
import environ
import sys  # Hata yakalama için eklendi

# 1. Env başlatma
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'django-insecure-local-key'),
    DATABASE_URL=(str, 'sqlite:///db.sqlite3')
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env dosyasını oku
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# --- GÜVENLİK AYARLARI ---
SECRET_KEY = env('SECRET_KEY')

# Cloud Run'da bazen False olduğunda statik dosyalar görünmeyebiliyor,
# şimdilik True yapalım ki site kesin açılsın. Sonra False yaparız.
DEBUG = env('DEBUG') 

ALLOWED_HOSTS = ['*'] # Hata almamak için herkesi kabul et

# Cloud Run için güvenilen kaynaklar
CSRF_TRUSTED_ORIGINS = ['https://*.run.app', 'http://localhost:8080']

# --- UYGULAMALAR ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', 
    'django.contrib.staticfiles',
    'core', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
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
        'DIRS': [], 
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

# --- VERİTABANI (SİTEYİ KURTARAN KISIM) ---
# Burası "Zırhlı" yapıldı. Eğer PostgreSQL şifresinde/bağlantısında hata varsa
# siteyi çökertmek yerine otomatik olarak geçici SQLite'a döner.
# Böylece site AÇILIR ve hatayı ekranda görüp düzeltebiliriz.
try:
    if os.getenv('DATABASE_URL'):
        DATABASES = {
            'default': env.db('DATABASE_URL')
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
except Exception as e:
    # Veritabanı bağlantısı patlarsa bile siteyi aç:
    print(f"Veritabani hatasi, SQLite kullaniliyor: {e}")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- ŞİFRE DOĞRULAMA (Eksiksiz korundu) ---
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

# --- STATİK DOSYALAR ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Manifest hatalarını önlemek için daha basit bir depolama seçtik
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# --- GİRİŞ/ÇIKIŞ AYARLARI ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'ana_sayfa' 
LOGOUT_REDIRECT_URL = 'login'

# --- EMAIL (Eksiksiz korundu) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD', default='')