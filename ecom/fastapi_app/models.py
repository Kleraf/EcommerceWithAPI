from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from .database import Base
import datetime


# ============================================================
# store.Product
# ============================================================
class Product(Base):
    __tablename__ = "store_product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(6, 2), default=0)
    category_id = Column(Integer, nullable=True)  # simplified
    description = Column(String(250), nullable=True)
    image = Column(String(250))
    is_sale = Column(Boolean, default=False)
    sale_price = Column(Numeric(6, 2), default=0)

    order_items = relationship("OrderItem", back_populates="product")


# ============================================================
# payment.Order
# ============================================================
class PaymentOrder(Base):
    __tablename__ = "payment_order"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    full_name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    shipping_address = Column(Text, nullable=False)
    amount_paid = Column(Numeric(7, 2), nullable=False)
    date_oredered = Column(DateTime, default=datetime.datetime.utcnow)
    shipped = Column(Boolean, default=False)
    date_shipped = Column(DateTime, nullable=True)

    items = relationship("OrderItem", back_populates="order")


# ============================================================
# payment.OrderItem
# ============================================================
class OrderItem(Base):
    __tablename__ = "payment_orderitem"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("payment_order.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("store_product.id"), nullable=True)
    user_id = Column(Integer, nullable=True)

    quantity = Column(Integer, default=1)
    price = Column(Numeric(7, 2), nullable=False)

    order = relationship("PaymentOrder", back_populates="items")
    product = relationship("Product", back_populates="order_items")
