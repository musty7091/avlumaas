# 1. Python Sürümü
FROM python:3.10-slim

# 2. Python ayarları (Hızlı log görmek için)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Çalışma klasörünü ayarla
WORKDIR /app

# 4. Gerekli kütüphaneleri yükle
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5. Proje dosyalarını kopyala
COPY . /app/

# 6. Port Değişkeni (Google Cloud bunu otomatik verir ama biz tanımlayalım)
ENV PORT 8080

# 7. BAŞLATMA KOMUTU (SİHİRLİ KISIM BURASI)
# Gunicorn kullanarak başlatır, 0.0.0.0 adresini dinler.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 avlu_backend.wsgi:application