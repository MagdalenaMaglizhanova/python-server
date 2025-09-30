# 1. Използваме малък Python образ
FROM python:3.11-slim

# 2. Създаваме директория за приложението
WORKDIR /app

# 3. Инсталираме зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копираме целия проект
COPY . .

# 5. Отваряме порт
EXPOSE 8000

# 6. Стартираме приложението с uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
