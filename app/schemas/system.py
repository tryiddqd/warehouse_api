from pydantic import BaseModel, Field, field_validator

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class EchoRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=255)
    uppercase: bool = False
    times: int = Field(1, ge=1, le=10)

class EchoResponse(BaseModel):
    message: str
    length: int