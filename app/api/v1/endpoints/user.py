from app.core.security import JWTBearer,RoleChecker, decode_access_token, get_current_user
from app.services.user_service import delete_user_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.schemas.user import UserResponse, UserUpdateAdmin, UserUpdateSelf, UserAuthPayload
from app.services.user_service import get_user_service, update_user_admin_service,update_user_self_service
from app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

allow_admin = RoleChecker(["admin"])


#MAKE SURE THE USER CAN GET ONLY AND INLY HIS OWN ACCOUNT NOT OTHERS
@router.get("/{id}", response_model=UserResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
def get_user(id,current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_service(db,id)

@router.get("/me", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
def get_me_user(current_user: UserAuthPayload = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_service(db,current_user.id)


@router.put("/me/{id}", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
def update_me(id,payload : UserUpdateSelf, db: Session = Depends(get_db)):
    updated = update_user_self_service(db,id,payload)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated

@router.put("/me/{id}", response_model=UserResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
def update_user(id,payload : UserUpdateAdmin, db: Session = Depends(get_db)):
    updated = update_user_admin_service(db,id,payload)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated

@router.delete("/{order_id}", status_code=204,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
def delete_user(order_id,db: Session = Depends(get_db)):
    deleted = delete_user_service(db,order_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return

