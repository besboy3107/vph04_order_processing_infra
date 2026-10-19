FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

# Приложение приватное: слушает внутри docker-сети, наружу его пускает только nginx (/api).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
