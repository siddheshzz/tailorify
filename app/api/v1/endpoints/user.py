from app.core.security import JWTBearer, decode_access_token
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.schemas.user import UserResponse, UserUpdateSelf
from app.services.user_service import get_user_service,update_user_self_service
from app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()


@router.get("/{id}", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
def get_user(id, db: Session = Depends(get_db)):
    return get_user_service(db,id)

@router.put("/{id}", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
def update_user(id,payload : UserUpdateSelf, db: Session = Depends(get_db)):
    updated = update_user_self_service(db,id,payload)

    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return updated

# @router.delete("/{order_id}", status_code=204,dependencies=[Depends(JWTBearer())])
# def delete_order(order_id,db: Session = Depends(get_db)):
#     deleted = delete_order_service(db,order_id)

#     if not deleted:
#         raise HTTPException(status_code=404, detail="Order not found")
    
#     return

