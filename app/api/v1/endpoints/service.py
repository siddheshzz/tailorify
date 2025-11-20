from app.core.security import JWTBearer, decode_access_token
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.schemas.service import ServiceCreate, ServiceResponse
from app.services.service import create_service, get_services
from app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=ServiceResponse,dependencies=[Depends(JWTBearer())])
def add_service(service: ServiceCreate, db: Session = Depends(get_db)):
    return create_service(db, service)

# @router.get("/", response_model=List[ServiceResponse])
# def list_services(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     if not credentials:
#         raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Cred missing")
    
#     token  = credentials.credentials
#     payload = decode_access_token(token)

#     if not payload:
#         raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="INvalid or expired token missing")
    
#     return get_services(db, skip, limit)

@router.get("/", response_model=List[ServiceResponse],dependencies=[Depends(JWTBearer())])
def list_services(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_services(db, skip, limit)
