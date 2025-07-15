from pydantic import BaseModel

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
