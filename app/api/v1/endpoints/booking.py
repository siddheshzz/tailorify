from uuid import UUID
from fastapi import APIRouter, Depends,  status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import BookingServiceDep
from app.schemas.booking import BookingCreate, BookingResponse
# from app.services.booking_service import create_booking, get_bookings_by_user
from app.models.user import User
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer


from app.core.security import SECRET_KEY, ALGORITHM, JWTBearer, decode_access_token, get_current_user
from app.core.security import create_access_token
router = APIRouter()


@router.post("/", response_model=BookingResponse, dependencies=[Depends(JWTBearer())])
async def make_booking(
    booking: BookingCreate,
    service: BookingServiceDep,
    current_user: User = Depends(get_current_user),
):
    user_id = getattr(current_user,"id")
    return await service.add( booking, UUID(user_id))

@router.get("/", response_model=List[BookingResponse],dependencies=[Depends(JWTBearer())])
async def list_bookings(
    service: BookingServiceDep,
    current_user: User = Depends(get_current_user),
):
    user_id = getattr(current_user,"id")
    return await service.get_bookings_by_user( user_id)
