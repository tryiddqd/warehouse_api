from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate
from app.crud import order as crud_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderRead)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return crud_order.create_order(db, order)

@router.get("/", response_model=List[OrderRead])
def read_orders(db: Session = Depends(get_db)):
    return crud_order.get_orders(db)

@router.get("/{order_id}", response_model=OrderRead)
def read_order(order_id: int, db: Session = Depends(get_db)):
    return crud_order.get_order(db, order_id)


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_status(order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)):
    return crud_order.update_order_status(db, order_id, status_update.status)
