from sqlalchemy.orm import Session
from app.models.service import Service
from app.schemas.service import ServiceCreate

def create_service(db: Session, service: ServiceCreate):
    db_service = Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_services(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Service).offset(skip).limit(limit).all()
