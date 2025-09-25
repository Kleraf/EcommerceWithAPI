from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_app.database import SessionLocal
from . import models
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# Do not auto-create tables; rely on Django migrations / existing schema

app = FastAPI(title="E-commerce API")

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# GET API: All items / Item by ID
# ============================================================
@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Product).filter(models.Product.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# ============================================================
# GET API: All sales transactions (Orders)
# ============================================================
@app.get("/sales")
def get_sales(db: Session = Depends(get_db)):
    return db.query(models.PaymentOrder).all()


# ============================================================
# POST API: Add an order (purchase)
# ============================================================
class OrderItemIn(BaseModel):
    product_id: int
    quantity: int
    price: Decimal


class OrderIn(BaseModel):
    user_id: Optional[int] = None
    full_name: str = Field(...)
    email: str = Field(...)
    shipping_address: str = Field(...)
    amount_paid: Decimal = Field(...)
    items: List[OrderItemIn] = []


@app.post("/orders")
def add_order(order: OrderIn, db: Session = Depends(get_db)):
    new_order = models.PaymentOrder(
        user_id=order.user_id,
        full_name=order.full_name,
        email=order.email,
        shipping_address=order.shipping_address,
        amount_paid=order.amount_paid
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Add order items
    for item in order.items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            user_id=order.user_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(order_item)
    db.commit()

    return {"message": "Order created", "order_id": new_order.id}


# ============================================================
# PUT API: Update an order (quantity, status)
# ============================================================
class UpdateOrderItemIn(BaseModel):
    product_id: int
    quantity: Optional[int] = None
    price: Optional[Decimal] = None


class UpdateOrderIn(BaseModel):
    shipped: Optional[bool] = None
    date_shipped: Optional[datetime] = None
    items: Optional[List[UpdateOrderItemIn]] = None


@app.put("/orders/{order_id}")
def update_order(order_id: int, update_data: UpdateOrderIn, db: Session = Depends(get_db)):
    order = db.query(models.PaymentOrder).filter(models.PaymentOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update status fields
    if update_data.shipped is not None:
        order.shipped = update_data.shipped
    if update_data.date_shipped is not None:
        order.date_shipped = update_data.date_shipped
    # Auto-set date_shipped when shipped flips to True and not provided
    if order.shipped and order.date_shipped is None:
        order.date_shipped = datetime.utcnow()

    # Update quantities in OrderItem
    if update_data.items is not None:
        for item in update_data.items:
            order_item = db.query(models.OrderItem).filter(
                models.OrderItem.order_id == order_id,
                models.OrderItem.product_id == item.product_id
            ).first()
            if order_item:
                if item.quantity is not None:
                    order_item.quantity = item.quantity
                if item.price is not None:
                    order_item.price = item.price

    db.commit()
    db.refresh(order)
    return {"message": "Order updated", "order": order}


# ============================================================
# DELETE API: Delete an order
# ============================================================
@app.delete("/orders/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.PaymentOrder).filter(models.PaymentOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

# Seed endpoint removed per requirement
