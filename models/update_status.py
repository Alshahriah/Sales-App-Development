from pydantic import BaseModel

class UpdateStatusRequest(BaseModel):
    delivery_status: str
