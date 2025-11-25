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


def get_service_by_id(id,db: Session, skip: int = 0, limit: int = 10):
    service = db.query(Service).filter(Service.id == id).first()
    # if service is None:
    #     raise HTTPException(status_code=404,detail="User not found")
    return service

