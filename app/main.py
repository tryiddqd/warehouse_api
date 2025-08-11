from fastapi import FastAPI
from app.api import product as product_router
from dotenv import load_dotenv
load_dotenv()


from app.models import product
from app.core.database import engine, Base
from app.api import order as order_router
from app.core.logging import setup_logging
setup_logging()

app = FastAPI()


app.include_router(product_router.router)
app.include_router(order_router.router)
@app.get("/")
def root():
    return {"message": "Warehouse API is running"}
