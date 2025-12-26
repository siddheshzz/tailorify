from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

# from fastapi import Depends, HTTP
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.user import UserAuthPayload

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    # expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


class JWTBearer(HTTPBearer):
    """
    Standardized JWT Bearer dependency that validates the token
    and returns the payload.
    """

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )

        if not credentials:
            raise HTTPException(status_code=403, detail="Not authenticated")

        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=403, detail="Invalid authentication scheme."
            )

            # Decode the JWT here
        payload = decode_access_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=403, detail="Invalid or expired token.")
        return payload


def get_token_payload(auth: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    This is the core dependency. It handles the extraction and decoding.
    It's type-safe because it doesn't override base classes.
    """
    payload = decode_access_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return payload


def get_current_user(payload: dict = Depends(get_token_payload)) -> UserAuthPayload:
    user_id = payload.get("user_id")
    user_type = payload.get("user_type")
    user_email = payload.get("user_email")

    if not user_id or not user_type:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token payload is missing required user identity fields.",
        )
    return UserAuthPayload(
        id=str(user_id),
        email=user_email,
        user_type=user_type,
    )


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: UserAuthPayload = Depends(get_current_user)):
        if current_user.user_type not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        # If successful, return the payload (or the user object if you prefer)
        return current_user
