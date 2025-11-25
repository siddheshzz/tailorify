from app.core.security import JWTBearer, decode_access_token
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import create_order_service, get_orders
from app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=OrderResponse,dependencies=[Depends(JWTBearer())])
def create_order(service: OrderCreate, db: Session = Depends(get_db)):
    return create_order_service(db, service)


@router.get("/", response_model=List[OrderResponse],dependencies=[Depends(JWTBearer())])
def list_order(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_orders(db, skip, limit)
