
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductSearch, PageParams
from typing import Sequence

# Создание или обновление существующего продукта
async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    """
    Атомарно: вставить товар, а при конфликте по name — увеличить quantity.
    price/description при конфликте не трогаем.
    """
    stmt = (
        insert(Product)
        .values(
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
        )
        .on_conflict_do_update(
            index_elements=[Product.name],  # уникальный ключ
            set_={
                "quantity": Product.quantity + product.quantity,
                # если решишь обновлять:
                # "price": product.price,
                # "description": product.description,
            },
        )
        .returning(Product.id)
    )

    res = await db.execute(stmt)
    product_id = res.scalar_one()          # вернули id вставленной/обновлённой строки
    await db.commit()
    return await db.get(Product, product_id)

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

SORT_MAP = {
    "id": Product.id,
    "name": Product.name,
    "price": Product.price,
    "quantity": Product.quantity,
}

async def search_products(db: AsyncSession, product_search: ProductSearch, page_params: PageParams) -> tuple[Sequence[Product], int]:
    col = SORT_MAP[page_params.sort_by]
    order_expr = col.desc() if page_params.sort_order == "desc" else col.asc()
    conds = []

    if product_search.q is not None:
        conds.append(Product.name.ilike(f"%{product_search.q}%"))

    if product_search.min_price is not None:
        conds.append(Product.price >= product_search.min_price)

    if product_search.max_price is not None:
        conds.append(Product.price <= product_search.max_price)

    stmt = select(Product)
    if conds:
        stmt = stmt.where(*conds)
    stmt = stmt.order_by(order_expr).offset(page_params.offset).limit(page_params.limit)
    result = await db.execute(stmt)
    items = result.scalars().all()

    count_stmt = select(func.count()).select_from(Product)
    if conds:
        count_stmt = count_stmt.where(*conds)

    total = await db.scalar(count_stmt)

    return items, int(total or 0)


async def list_products(
    db: AsyncSession,
    *,
    page_params: PageParams
) -> tuple[Sequence[Product], int]:
    col = SORT_MAP[page_params.sort_by]
    order_expr = col.desc() if page_params.sort_order == "desc" else col.asc()

    total = await db.scalar(select(func.count()).select_from(Product))
    result = await db.execute(
        select(Product).order_by(order_expr).offset(page_params.offset).limit(page_params.limit)
    )
    items = result.scalars().all()
    return items, int(total or 0)