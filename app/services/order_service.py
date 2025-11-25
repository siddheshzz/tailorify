from uuid import UUID
from sqlalchemy.orm import Session
from app.models.order import Order
from app.schemas.order import OrderCreate

def create_order_service(db: Session, order: OrderCreate):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Order).offset(skip).limit(limit).all()


def get_order_by_id(order_id:UUID , db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()

    return order


def update_order_service(db:Session,order_id:UUID, payload:OrderCreate):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        return None

    for field, value in payload.dict().items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return order


def delete_order_service( db:Session,order_id: UUID,):
    order = db.query(Order).filter(Order.id == order_id).first()

    db.delete(order)
    db.commit()

    return True
