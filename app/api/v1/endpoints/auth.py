from fastapi import APIRouter, HTTPException

from app.core.dependencies import UserServiceDep
from app.core.security import create_access_token
from app.schemas.auth import Token, UserCreate, UserLogin

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(user: UserCreate, service: UserServiceDep):
    user = await service.add(user)
    # user = create_user(user,db)
    token = create_access_token(
        {"user_email": user.email, "user_type": user.user_type, "user_id": str(user.id)}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, service: UserServiceDep):
    user = await service.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(
        {"user_email": user.email, "user_type": user.user_type, "user_id": str(user.id)}
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    # Just tells client to delete token
    return {"message": "Successfully logged out. Please remove token on client side."}
