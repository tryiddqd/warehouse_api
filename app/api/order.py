from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import logging
import uuid

from app.core.database import get_db
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate
from app.crud import order as crud_order

router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=OrderRead)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    trace_id = str(uuid.uuid4())
    logger.info("[%s] ➕ Incoming create_order request from customer: %s", trace_id, order.customer_name)

    try:
        result = crud_order.create_order(db, order, trace_id=trace_id)
        logger.info("[%s] ✅ Order created successfully with total: %.2f", trace_id, result.total_price)
        return result

    except HTTPException as e:
        logger.warning("[%s] ⚠️ Business validation failed (%d): %s", trace_id, e.status_code, e.detail)
        raise

    except Exception as e:
        logger.exception("[%s] ❌ Order creation failed: %s", trace_id, str(e))
        raise

@router.get("/", response_model=List[OrderRead])
def read_orders(db: Session = Depends(get_db)):
    return crud_order.get_orders(db)

@router.get("/{order_id}", response_model=OrderRead)
def read_order(order_id: int, db: Session = Depends(get_db)):
    return crud_order.get_order(db, order_id)

# ✅ Добавляем недостающий PATCH-эндпоинт
@router.patch("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)):
    return crud_order.update_order_status(db, order_id, status_update.status)

# ✅ Добавляем недостающий DELETE-эндпоинт
@router.delete("/{order_id}", response_model=OrderRead)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = crud_order.delete_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderRead.model_validate(order)

@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status_route(order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)):
    return crud_order.update_order_status(db, order_id, status_update.status)