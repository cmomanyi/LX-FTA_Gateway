from pydantic import BaseModel


class AttackRequest(BaseModel):
    sensor_id: str
