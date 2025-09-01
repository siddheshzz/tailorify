from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.service import ServiceCreate, ServiceResponse
from app.services.service import create_service, get_services
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=ServiceResponse)
def add_service(service: ServiceCreate, db: Session = Depends(get_db)):
    return create_service(db, service)

@router.get("/", response_model=List[ServiceResponse])
def list_services(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_services(db, skip, limit)
