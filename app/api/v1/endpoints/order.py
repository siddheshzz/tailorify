from app.core.security import JWTBearer, decode_access_token
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import create_order_service, get_orders, get_order_by_id, update_order_service,delete_order_service
from app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=OrderResponse,dependencies=[Depends(JWTBearer())])
def create_order(service: OrderCreate, db: Session = Depends(get_db)):
    return create_order_service(db, service)


@router.get("/", response_model=List[OrderResponse],dependencies=[Depends(JWTBearer())])
def list_order(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_orders(db, skip, limit)

@router.get("/{order_id}", response_model=OrderResponse,dependencies=[Depends(JWTBearer())])
def get_order(order_id, db: Session = Depends(get_db)):
    return get_order_by_id(order_id,db)

@router.put("/{order_id}", response_model=OrderResponse,dependencies=[Depends(JWTBearer())])
def update_order(order_id,payload : OrderCreate, db: Session = Depends(get_db)):
    updated = update_order_service(db,order_id,payload)

    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return updated

@router.delete("/{order_id}", status_code=204,dependencies=[Depends(JWTBearer())])
def delete_order(order_id,db: Session = Depends(get_db)):
    deleted = delete_order_service(db,order_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return

