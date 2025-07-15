from pydantic import BaseModel, Field, validator
from typing import Optional


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Носки")
    description: Optional[str] = Field(None, max_length=300, example="Теплые зимние носки")
    price: float = Field(..., gt=0, example=199.99)
    quantity: int = Field(..., ge=0, example=100)

    # Нормализация имени — убираем лишние пробелы и приводим к одному регистру (если нужно)
    @validator("name", pre=True)
    def normalize_name(cls, v: str) -> str:
        return v.strip()


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True
