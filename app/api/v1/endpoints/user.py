from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import UserServiceDep
from app.core.security import (
    RoleChecker,
    create_access_token,
    get_current_user,
)
from app.schemas.user import (
    Token,
    UserAuthPayload,
    UserCreate,
    UserLogin,
    UserResponse,
    UserRole,
    UserUpdateAdmin,
    UserUpdateSelf,
)

router = APIRouter()
# security = HTTPBearer()

allow_admin = RoleChecker(["admin"])


# ---- AUTHENTICATION (PUBLIC) ---- #
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, service: UserServiceDep):
    # Ensure role is always client on public registration
    user_in.user_type = UserRole.CLIENT
    user = await service.add(user_in)

    token = create_access_token({"sub": str(user.id), "role": user.user_type})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, service: UserServiceDep):
    user = await service.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token(
        {"user_email": user.email, "user_type": user.user_type, "user_id": str(user.id)}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    service: UserServiceDep, current_user: UserAuthPayload = Depends(get_current_user)
):
    id = UUID(current_user.id)
    return await service.get(id)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    payload: UserUpdateSelf,
    service: UserServiceDep,
    current_user=Depends(get_current_user),
):
    id = UUID(current_user.id)
    updated = await service.update_user_self_service(id, payload)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return updated


# ---- ADMIN ACTIONS (PROTECTED) ---- #


# MAKE SURE THE USER CAN GET ONLY AND INLY HIS OWN ACCOUNT NOT OTHERS
@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: UUID, service: UserServiceDep, admin: UserAuthPayload = Depends(allow_admin)
):
    return await service.get(id)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    service: UserServiceDep, admin: UserAuthPayload = Depends(allow_admin)
):
    return await service.getAll()


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id,
    payload: UserUpdateAdmin,
    service: UserServiceDep,
    admin: UserAuthPayload = Depends(allow_admin),
):
    updated = await service.update_user_admin_service(id, payload)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return updated


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id, service: UserServiceDep, admin: UserAuthPayload = Depends(allow_admin)
):
    deleted = await service.delete_user_service(user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")

    return
