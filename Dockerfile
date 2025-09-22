# Използваме стабилна Python версия
FROM python:3.11-slim

# Инсталираме системни зависимости за Pillow и Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-bul \
    tesseract-ocr-eng \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Създаваме работна директория
WORKDIR /app

# Копираме requirements
COPY requirements.txt .

# Инсталираме dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копираме целия код
COPY . .

# Start command
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000", "--workers", "4"]
