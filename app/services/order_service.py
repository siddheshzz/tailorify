from uuid import UUID
from sqlalchemy.orm import Session
from app.models.order import Order
from app.schemas.order import OrderCreate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging


logger = logging.getLogger(__name__)


def create_order_service(db: Session, order: OrderCreate):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Order).offset(skip).limit(limit).all()


def get_orders_me(db: Session,current_id, skip: int = 0, limit: int = 10):
    return db.query(Order).filter(Order.client_id == current_id).offset(skip).limit(limit).all()

def get_order_by_id_me(order_id:UUID , db: Session, current_id):
    try:
        order = db.query(Order).filter(Order.id == order_id).filter(Order.client_id==UUID(current_id)).first()
        return order
    except IntegrityError as e:
        logger.warning(f"Integrity error when creating service: {e}")
        # raise DuplicateResourceError("Service with this name/detail already exists.")
    except SQLAlchemyError as e:
        # db.rollback() # Rollback for any other DB error
        logger.error(f"Database error during service creation: {e}")
        # Raise a generic DB error that the API layer will handle

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

# def order_image(db:Session,order_id):
#      # Check order exists
#     order = db.query(Order).filter(Order.id == order_id).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")

#     # Upload image
#     saved_image = upload_order_image(db, order_id, file, order)
#     return saved_image


def delete_order_service( db:Session,order_id: UUID,):
    order = db.query(Order).filter(Order.id == order_id).first()

    db.delete(order)
    db.commit()

    return True
