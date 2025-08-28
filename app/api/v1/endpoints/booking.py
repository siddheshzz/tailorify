from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import create_booking, get_bookings_by_user
from app.db.session import get_db
from app.models.user import User

# TODO: replace with real JWT auth
def get_current_user():
    return User(id=1, email="demo@user.com")

router = APIRouter()

@router.post("/", response_model=BookingResponse)
def make_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_booking(db, booking, current_user.id)

@router.get("/", response_model=List[BookingResponse])
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_bookings_by_user(db, current_user.id)
