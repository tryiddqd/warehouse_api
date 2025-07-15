from fastapi import FastAPI
from app.api import product as product_router


from app.models import product
from app.core.database import engine, Base
from app.api import order as order_router


app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(product_router.router)
app.include_router(order_router.router)
@app.get("/")
def root():
    return {"message": "Warehouse API is running"}
