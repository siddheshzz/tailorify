from typing import Annotated
# from fastapi import Depends, HTTP
from passlib.context import CryptContext
from jose import jwt,JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta

SECRET_KEY = "very-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()
def get_password_hash(password):
    print("PASSWORD LENGTH:", len(password.encode("utf-8")))
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
# def jwt_Required(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     if not credentials:
#         raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Cred missing")
    
#     token  = credentials.credentials
#     payload = decode_access_token(token)

#     if not payload:
#         raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="INvalid or expired token missing")
    
#     return get_services(db, skip, limit)


# app/auth/auth_bearer.py

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials



class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            # Decode the JWT here
            payload = decode_access_token(credentials.credentials)
            if payload is None:
                raise HTTPException(status_code=403, detail="Invalid or expired token.")

            return payload   # <-- return dict
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_access_token(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid
    def verified_load(self, jwtoken: str):
        isTokenValid: bool = False

        try:
            payload = decode_access_token(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return payload

from fastapi import Depends, HTTPException, status
from typing import List


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, payload: dict = Depends(JWTBearer())):
        
        # Extract the role from the token payload
        user_role = payload.get("user_type")

        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Operation not permitted: Insufficient privileges"
            )
        
        # If successful, return the payload (or the user object if you prefer)
        return payload