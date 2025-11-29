from app.core.security import JWTBearer, decode_access_token, RoleChecker
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.schemas.service import ServiceCreate, ServiceResponse
from app.services.service import create_service, get_services, get_service_by_id
from app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


allow_admin = RoleChecker("admin")
router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=ServiceResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
def add_service(service: ServiceCreate, db: Session = Depends(get_db)):
    return create_service(db, service)

@router.get("/", response_model=List[ServiceResponse],dependencies=[Depends(JWTBearer())])
def list_services(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_services(db, skip, limit)

@router.get("/{id}", response_model=ServiceResponse,dependencies=[Depends(JWTBearer())])
def get_service(id, db: Session = Depends(get_db)):
    return get_service_by_id(id,db)

# @router.put("/{id}", response_model=ServiceResponse,dependencies=[Depends(JWTBearer())])
# def update_service(id,skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     return get_service_by_id(id,db,skip,limit)


