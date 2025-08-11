import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatusEnum

logger = logging.getLogger(__name__)

async def create_order(db: AsyncSession, order_data: OrderCreate, trace_id: str = "-"):
    if not order_data.items:
        logger.warning("[%s] 🚫 Empty order received", trace_id)
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    order = Order(customer_name=order_data.customer_name)
    db.add(order)
    await db.flush()  # Получаем order.id

    total_price = 0.0

    for item_data in order_data.items:
        result = await db.execute(select(Product).filter(Product.id == item_data.product_id))
        product = result.scalar_one_or_none()
        if not product:
            logger.warning("[%s] ❌ Product ID %s not found", trace_id, item_data.product_id)
            raise HTTPException(status_code=404, detail=f"Product ID {item_data.product_id} not found")

        if product.quantity < item_data.quantity:
            logger.warning("[%s] ❗ Not enough stock for product %s (have %d, need %d)", trace_id, product.name, product.quantity, item_data.quantity)
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")

        product.quantity -= item_data.quantity
        total_price += product.price * item_data.quantity

        logger.info("[%s] 🛒 Reserved %d of %s for order %d", trace_id, item_data.quantity, product.name, order.id)

        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity
        )
        db.add(order_item)

    order.total_price = total_price
    logger.info("[%s] 💰 Total price for order %d calculated: %.2f", trace_id, order.id, total_price)

    await db.commit()

    # 🔁 Вместо await db.refresh(order), сразу делаем полную выборку с нужными связями
    stmt = select(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product)
    ).where(Order.id == order.id)

    result = await db.execute(stmt)
    order_with_items = result.unique().scalar_one()

    return order_with_items

async def get_orders(db: AsyncSession):
    result = await db.execute(select(Order).options(joinedload(Order.items)))
    return result.scalars().all()

async def get_order(db: AsyncSession, order_id: int):
    result = await db.execute(
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id)
    )
    order = result.unique().scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

async def update_order_status(db: AsyncSession, order_id: int, new_status: OrderStatusEnum):
    result = await db.execute(select(Order).options(joinedload(Order.items)).filter(Order.id == order_id))
    order = result.unique().scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == OrderStatusEnum.cancelled:
        raise HTTPException(status_code=400, detail="Нельзя изменить отменённый заказ")

    if new_status == OrderStatusEnum.cancelled:
        for item in order.items:
            result = await db.execute(select(Product).filter(Product.id == item.product_id))
            product = result.unique().scalar_one_or_none()
            if product:
                product.quantity += item.quantity

    order.status = new_status
    await db.commit()
    await db.refresh(order)
    return order

async def delete_order(db: AsyncSession, order_id: int):
    result = await db.execute(select(Order).filter(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        return None
    await db.delete(order)
    await db.commit()
    return order
