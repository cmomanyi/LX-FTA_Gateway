from datetime import datetime

from fastapi import FastAPI, Request
import random

app = FastAPI(title="Secure Gateway API")
# CORS settings for frontend (e.g. React dev server)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



anomaly_logs = []

# connected_clients = []


@app.get("/")
def read_root():
    return {"message": "✅ Secure Gateway API is running."}


@app.get("/health")
def health():
    return {"status": "ok"}
