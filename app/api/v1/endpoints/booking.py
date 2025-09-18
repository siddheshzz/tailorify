from fastapi import APIRouter, Depends,  status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import create_booking, get_bookings_by_user
from app.db.session import get_db
from app.models.user import User
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer


from app.core.security import SECRET_KEY, ALGORITHM
from app.core.security import create_access_token
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# TODO: replace with real JWT auth
def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email== user_id).first()
    if user is None:
        raise credentials_exception

    return user



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
