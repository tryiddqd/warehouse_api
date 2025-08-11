from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.crud import product as product_crud
from app.schemas.product import ProductCreate, ProductRead
from app.core.database import get_db


router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.post("/", response_model=ProductRead)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await product_crud.create_product(db=db, product=product)

@router.get("/", response_model=List[ProductRead])
async def read_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await product_crud.get_products(db=db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductRead)
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