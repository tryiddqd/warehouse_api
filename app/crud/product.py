from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate


def create_product(db: Session, product: ProductCreate):
    # Проверка: есть ли товар с таким именем
    existing_product = db.query(Product).filter(Product.name == product.name).first()

    if existing_product:
        # Если есть — увеличиваем количество
        existing_product.quantity += product.quantity
        db.commit()
        db.refresh(existing_product)
        return existing_product

    # Если нет — создаём новый товар
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()

def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return product


def update_product(db: Session, product_id: int, update_data: ProductCreate):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    for key, value in update_data.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product
