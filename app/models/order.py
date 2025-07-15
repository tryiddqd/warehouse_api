from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class OrderStatusEnum(str, enum.Enum):
    pending = "в процессе"
    shipped = "отправлен"
    delivered = "доставлен"
    cancelled = "отменён"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    total_price = Column(Float, nullable=False, default=0.0)  # ← Рассчитывается по items
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с OrderItem
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")
