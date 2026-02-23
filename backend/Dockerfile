# Python 3.12 kurulu linux işletim sisteminden imajı oluştur
FROM python:3.12-slim

# Konteynır içinde bir app klasörü oluştur ve içine gir.
WORKDIR /app

#   logları terminalde görmek için
ENV PYTHONUNBUFFERED=1

# gerekli paketleri yukle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# tüm backend dosyalarını kopyala
COPY . .

# konteynır çalışınca suncucuyu başlat
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]