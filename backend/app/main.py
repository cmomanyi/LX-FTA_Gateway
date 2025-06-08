from fastapi import FastAPI, HTTPException
# from aws_services.aws_services import dynamodb_put_item
from app.aws_services.aws_services import dynamodb_put_item
from app.auth.auth import router as auth_router

app = FastAPI(title="LX-FTA_Gateway API")

# CORS settings for frontend (e.g. React dev server)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.post("/sensor")
async def save_sensor_data(payload: dict):
    try:
        response = dynamodb_put_item(payload)
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
