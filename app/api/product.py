from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from app.crud import product as product_crud
from app.schemas.product import (
    ProductCreate, ProductRead,
    ProductPage, ProductSearch,
    PageParams
)
from app.core.database import get_db


router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get("/list", response_model=ProductPage)
async def list_products(
    page_params: Annotated[PageParams, Depends()],
    db: AsyncSession = Depends(get_db),
):
    items, total = await product_crud.list_products(
        db, page_params=page_params
    )
    return ProductPage(
        items=[ProductRead.model_validate(i) for i in items],
        total=total, limit=page_params.limit, offset=page_params.offset
    )

@router.get("/search", response_model=ProductPage)
async def search_products(
        product_search: Annotated[ProductSearch, Depends()],
        page_params: Annotated[PageParams, Depends()],
        db: AsyncSession = Depends(get_db)):
    items, total =  await product_crud.search_products(db=db, product_search=product_search, page_params=page_params)
    return ProductPage(
        items=[ProductRead.model_validate(i) for i in items],
        total=total, limit=page_params.limit, offset=page_params.offset
    )


@router.post("/", response_model=ProductRead)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await product_crud.create_product(db=db, product=product)

@router.get("/", response_model=List[ProductRead])
async def read_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await product_crud.get_products(db=db, skip=skip, limit=limit)

@router.get("/{product_id:int}", response_model=ProductRead)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product = await product_crud.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=ProductRead)
async def update_product(product_id: int, product: ProductCreate, db: AsyncSession = Depends(get_db)):
    updated = await product_crud.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{product_id}", response_model=ProductRead)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await product_crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted

