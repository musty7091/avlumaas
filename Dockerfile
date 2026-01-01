# Python 3.10 tabanlı resmi imajı kullan
FROM python:3.10-slim

# Konteyner içinde çalışma dizini oluştur
WORKDIR /app

# Ortam değişkenlerini ayarla
# Python çıktılarının tamponlanmamasını sağlar (Logları anlık görmek için)
ENV PYTHONUNBUFFERED=1
# .pyc dosyalarının oluşmasını engeller
ENV PYTHONDONTWRITEBYTECODE=1

# Sistem bağımlılıklarını yükle (PostgreSQL ve diğerleri için gerekli kütüphaneler)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Gereksinim dosyasını kopyala ve kütüphaneleri yükle
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Proje dosyalarının tamamını kopyala
COPY . /app/

# Statik dosyaları topla (WhiteNoise için gerekli)
# Veritabanı bağlantısı olmadan çalışması için dummy env veriyoruz
RUN DATABASE_URL=sqlite:///db.sqlite3 python manage.py collectstatic --noinput

# Uygulamanın çalışacağı portu belirle (Cloud Run genelde 8080 kullanır)
ENV PORT=8080

# Uygulamayı Gunicorn ile başlat
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 avlu_backend.wsgi:application