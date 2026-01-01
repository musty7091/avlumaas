# 1. Python Sürümü
FROM python:3.10-slim

# 2. Ayarlar
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Çalışma klasörü
WORKDIR /app

# 4. Gerekli kütüphaneler (Postgres için)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Gereksinimleri yükle
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Kodları kopyala
COPY . /app/

# --- YENİ EKLENEN KISIM (CSS DÜZELTME) ---
# Statik dosyaları (CSS/JS) toplar. 
# Hata vermemesi için sahte bir SECRET_KEY tanımlıyoruz.
RUN SECRET_KEY=gecici-build-anahtari python manage.py collectstatic --noinput

# 7. Port ayarı
ENV PORT=8080

# 8. BAŞLATMA KOMUTU (GÜÇLENDİRİLMİŞ)
# Tabloları oluşturur -> Admin yoksa oluşturur -> Siteyi başlatır
CMD python manage.py migrate && \
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'm.mkaradeniz@gmail.com', 'admin123')" && \
    exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 avlu_backend.wsgi:application