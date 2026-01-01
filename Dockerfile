# 1. En kararlı Python sürümü
FROM python:3.10-slim

# 2. Python ayarları (Hızlı log görmek için)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Klasör ayarı
WORKDIR /app

# 4. PostgreSQL ve derleme araçlarını yükle
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Kütüphaneleri yükle
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Kodları kopyala
COPY . /app/

# 7. CSS dosyalarını topla (Admin paneli bozuk görünmesin)
RUN SECRET_KEY=gecici-build-anahtari python manage.py collectstatic --noinput

# 8. Portu aç
ENV PORT=8080

# 9. BAŞLATMA KOMUTU (SENİN ŞİFRENLE GÜNCELLENDİ)
# - Tabloları kur (migrate)
# - Admin kullanıcısını oluştur (Kullanıcı: Admin, Şifre: Mk91913632.,)
# - Siteyi başlat
CMD python manage.py migrate && \
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='Admin').exists() or User.objects.create_superuser('Admin', 'admin@avlu.com', 'Mk91913632.,')" && \
    exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 avlu_backend.wsgi:application