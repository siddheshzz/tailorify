from fastapi import APIRouter, HTTPException
from app.schemas.auth import UserCreate, UserLogin, Token
from app.services.user_service import create_user, authenticate_user
from app.core.security import create_access_token

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user: UserCreate):
    user = create_user(user)
    token = create_access_token({"user_email": user.email,"user_type":user.user_type,"user_id":str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(credentials: UserLogin):
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"user_email": user.email,"user_type":user.user_type,"user_id":str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    # Just tells client to delete token
    return {"message": "Successfully logged out. Please remove token on client side."}

    