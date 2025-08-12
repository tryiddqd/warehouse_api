from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Носки"})
    description: Optional[str] = Field(None, max_length=300, json_schema_extra={"example": "Теплые зимние носки"})
    price: float = Field(..., gt=0, json_schema_extra={"example": 199.99})
    quantity: int = Field(..., ge=0, json_schema_extra={"example": 100})

    # Нормализация имени — убираем лишние пробелы и приводим к одному регистру (если нужно)
    @field_validator("name", mode="before")
    def normalize_name(cls, v: str) -> str:
        return v.strip()


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

    model_config = {
        "from_attributes": True
    }

SortBy = Literal["id", "name", "price", "quantity"]
SortOrder = Literal["asc", "desc"]

class ProductPage(BaseModel):
    items: list[ProductRead]
    total: int
    limit: int
    offset: int