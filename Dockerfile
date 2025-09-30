# 1. Използваме малък Python образ
FROM python:3.11-slim

# 2. Създаваме директория за приложението
WORKDIR /app

# 3. Инсталираме зависимости (по-рано за по-добър кеш)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копираме целия проект
COPY . .

# 5. Отваряме порт (локален, Render ще го замести с $PORT)
EXPOSE 8000

# 6. Стартираме приложението с uvicorn
# Render задава $PORT автоматично -> използваме го
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
