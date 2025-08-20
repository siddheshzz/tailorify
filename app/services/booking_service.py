from sqlalchemy.orm import Session
from app.models.booking import Booking
from app.schemas.booking import BookingCreate

def create_booking(db: Session, booking: BookingCreate, user_id: int):
    db_booking = Booking(**booking.dict(), user_id=user_id)
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings_by_user(db: Session, user_id: int):
    return db.query(Booking).filter(Booking.user_id == user_id).all()
