from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatusEnum


def create_order(db: Session, order_data: OrderCreate):
    order = Order(customer_name=order_data.customer_name)
    db.add(order)
    db.flush()  # нужно получить order.id

    total_price = 0.0  # ← вот здесь

    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product ID {item_data.product_id} not found")

        if product.quantity < item_data.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")

        # Списываем остаток
        product.quantity -= item_data.quantity

        # Считаем цену для этой позиции и прибавляем к total
        total_price += product.price * item_data.quantity

        # Создаём OrderItem
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        db.add(order_item)

    # Сохраняем итоговую цену
    order.total_price = total_price

    db.commit()
    db.refresh(order)
    return order

def get_orders(db: Session):
    return db.query(Order).options(joinedload(Order.items)).all()

def get_order(db: Session, order_id: int):
    order = db.query(Order) \
        .options(joinedload(Order.items).joinedload(OrderItem.product)) \
        .filter(Order.id == order_id) \
        .first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

def update_order_status(db: Session, order_id: int, new_status: OrderStatusEnum):
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == OrderStatusEnum.cancelled and new_status != OrderStatusEnum.cancelled:
        raise HTTPException(status_code=400, detail="Нельзя изменить отменённый заказ")

    # Если отменяем — возвращаем товары
    if new_status == OrderStatusEnum.cancelled and order.status != OrderStatusEnum.cancelled:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.quantity += item.quantity

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order

