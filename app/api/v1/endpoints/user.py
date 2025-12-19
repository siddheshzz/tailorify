from uuid import UUID
from app.core.dependencies import UserServiceDep
from app.core.security import JWTBearer,RoleChecker, decode_access_token, get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.schemas.user import UserResponse, UserUpdateAdmin, UserUpdateSelf, UserAuthPayload
from app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

allow_admin = RoleChecker(["admin"])


@router.get("/me", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
async def get_me_user(service : UserServiceDep,current_user: UserAuthPayload = Depends(get_current_user)):
    id = UUID(current_user.id)
    return await service.get(id)


@router.put("/me/{id}", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
async def update_me(id:UUID,payload : UserUpdateSelf, service: UserServiceDep):
    updated = await service.update_user_self_service(id,payload)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated

#MAKE SURE THE USER CAN GET ONLY AND INLY HIS OWN ACCOUNT NOT OTHERS
@router.get("/{id}", response_model=UserResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
async def get_user(id:UUID, service: UserServiceDep,current_user: dict = Depends(get_current_user)):
    return await service.get(id)

@router.get("/", response_model=List[UserResponse],dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
async def get_users(service: UserServiceDep):
    return await service.getAll()

@router.put("/{id}", response_model=UserResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
async def update_user(id,payload : UserUpdateAdmin, service: UserServiceDep):
    updated = await service.update_user_admin_service(id,payload)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated

@router.delete("/{order_id}", status_code=204,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
async def delete_user(order_id, service: UserServiceDep):
    deleted = await service.delete_user_service(order_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return



