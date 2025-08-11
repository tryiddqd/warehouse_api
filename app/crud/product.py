from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Product
from app.schemas.product import ProductCreate

# Создание или обновление существующего продукта
async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    result = await db.execute(select(Product).where(Product.name == product.name))
    existing_product = result.scalar_one_or_none()

    if existing_product:
        existing_product.quantity += product.quantity
        await db.commit()
        await db.refresh(existing_product)
        return existing_product

    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

# Получение одного продукта по ID
async def get_product(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()

# Получение списка продуктов
async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()

# Удаление продукта
async def delete_product(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product:
        await db.delete(product)
        await db.commit()
    return product

# Обновление продукта
async def update_product(db: AsyncSession, product_id: int, update_data: ProductCreate):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        return None

    for key, value in update_data.model_dump().items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product