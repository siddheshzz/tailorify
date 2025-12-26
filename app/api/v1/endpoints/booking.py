from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import BookingServiceDep
from app.core.security import (
    JWTBearer,
    get_current_user,
)

# from app.services.booking_service import create_booking, get_bookings_by_user
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse

router = APIRouter()


@router.post("/", response_model=BookingResponse, dependencies=[Depends(JWTBearer())])
async def make_booking(
    booking: BookingCreate,
    service: BookingServiceDep,
    current_user: User = Depends(get_current_user),
):
    user_id = getattr(current_user, "id")
    return await service.add(booking, UUID(user_id))


@router.get(
    "/", response_model=List[BookingResponse], dependencies=[Depends(JWTBearer())]
)
async def list_bookings(
    service: BookingServiceDep,
    current_user: User = Depends(get_current_user),
):
    user_id = getattr(current_user, "id")
    return await service.get_bookings_by_user(user_id)
