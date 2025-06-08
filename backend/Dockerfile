FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app

# Copy entire backend folder contents, including app/
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Use official base image
#FROM python:3.10-slim
#
## Set working directory inside container
#WORKDIR /app
#
## Copy only requirements first to leverage Docker cache
#COPY requirements.txt .
#
## Install dependencies
#RUN pip install --no-cache-dir -r requirements.txt
#
## Copy the full backend code into the container
#COPY . .
#
## Expose FastAPI port
#EXPOSE 8000
#
## Start FastAPI app using uvicorn, targeting `app.main:app`
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
