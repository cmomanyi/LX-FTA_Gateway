FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app

# Copy entire backend folder contents, including app/
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
