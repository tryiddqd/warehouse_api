from fastapi import APIRouter, Query


from app.schemas.system import HealthResponse, EchoResponse, EchoRequest

router = APIRouter(
    prefix= "/system",
    tags=["system"]
)

@router.get("/healthz", response_model=HealthResponse)
async def check_health() -> HealthResponse:
    return HealthResponse(status="OK", service="warehouse api", version="0.1")

@router.post("/echo", response_model=EchoResponse)
async def echo(payload: EchoRequest) -> EchoResponse:
    text = payload.message.upper() if payload.uppercase else payload.message
    text = text * payload.times
    return EchoResponse(message=text, length=len(text))