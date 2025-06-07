# Dockerfile
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Set working directory inside the container
WORKDIR /app

# Copy everything inside backend into /app
COPY ./app /app/app
COPY requirements.txt .

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
