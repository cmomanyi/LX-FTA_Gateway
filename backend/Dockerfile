# Use official FastAPI base image with Uvicorn + Gunicorn
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Set working directory
WORKDIR /app

# Copy requirements first (to leverage Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (assuming it's in ./app folder)
COPY ./app ./app

# Expose port (optional but good practice)
EXPOSE 8000

# Set the default command to run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
