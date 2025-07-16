from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List

from app.schemas.order_item import OrderItemCreate
from app.models.order import OrderStatusEnum

class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum

    @field_validator("status", mode="before")
    def normalize_status(cls, v: str):
        # Приводим к нижнему регистру и заменяем "ё" на "е"
        normalized = v.lower().replace("ё", "е")
        mapping = {
            "в процессе": OrderStatusEnum.pending,
            "отправлен": OrderStatusEnum.shipped,
            "доставлен": OrderStatusEnum.delivered,
            "отменен": OrderStatusEnum.cancelled,  # <- обрабатывает и "отменён"
        }
        if normalized not in mapping:
            raise ValueError("Недопустимый статус заказа")
        return mapping[normalized]

class OrderCreate(BaseModel):
    customer_name: str
    items: List[OrderItemCreate]


class OrderItemRead(OrderItemCreate):
    id: int

    model_config = {
        "from_attributes":True
    }


class OrderRead(BaseModel):
    id: int
    customer_name: str
    created_at: datetime
    status: OrderStatusEnum
    items: List[OrderItemRead]

    model_config = {
        "from_attributes": True
    }