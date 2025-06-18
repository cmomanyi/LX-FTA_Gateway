from pydantic import BaseModel
from typing import Optional


class FirmwareUpload(BaseModel):
    sensor_id: str
    firmware_content: Optional[str] = None
    firmware_signature: Optional[str] = None