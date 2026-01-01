# 1. Python Sürümü
FROM python:3.10-slim

# 2. Ayarlar
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Klasör
WORKDIR /app

# 4. Kütüphaneler
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5. Dosyalar
COPY . /app/

# --- EKLENEN SATIR ---
# WhiteNoise için statik dosyaları topluyoruz
RUN python manage.py collectstatic --noinput
# ---------------------

# 6. Port
ENV PORT 8080

# 7. BAŞLATMA KOMUTU
# Migrate komutu burada olduğu için, her dağıtımda tabloları otomatik kontrol edecek.
CMD python manage.py migrate && exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 avlu_backend.wsgi:application