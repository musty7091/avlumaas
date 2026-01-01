# 1. Python Sürümü (Hafif sürüm)
FROM python:3.10-slim

# 2. Python ayarları (Logları anlık görmek için şart)
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

# 6. Port Değişkeni (Google Cloud için)
ENV PORT 8080

# 7. BAŞLATMA KOMUTU (SİHİRLİ SATIR BURASI) ⚠️
# Bu satır olmazsa "Listen" hatası alırsınız.
# Siteyi 0.0.0.0 adresinden dış dünyaya açar.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 avlu_backend.wsgi:application