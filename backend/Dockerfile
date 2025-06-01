# Dockerfile
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app

COPY ./app /app
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt
