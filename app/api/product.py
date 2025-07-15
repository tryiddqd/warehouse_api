from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud
from app.crud.product import create_product
from app.schemas.product import ProductCreate, ProductRead
from app.models import product as product_model
from app.deps.db import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.post("/", response_model=ProductRead)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return crud.product.create_product(db=db, product=product)

@router.get("/", response_model=List[ProductRead])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.product.get_products(db=db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductRead)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.product.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    updated = crud.product.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}", response_model=ProductRead)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.product.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted