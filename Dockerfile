# Използваме официален Python образ
FROM python:3.11-slim

# Задаваме директория за приложението
WORKDIR /app

# Копираме файловете с зависимостите
COPY requirements.txt .

# Инсталираме зависимостите
RUN pip install --no-cache-dir -r requirements.txt

# Копираме целия код
COPY ./app ./app

# Отваряме порт 10000
EXPOSE 10000

# Стартираме Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
