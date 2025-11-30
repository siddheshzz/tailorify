from app.models.user import User
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import datetime
from app.schemas.user import UserUpdateAdmin, UserUpdateSelf


def create_user(user_data):
    db = SessionLocal()
    time = datetime.now()
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        user_type = 'client',
        is_active = True,
        created_at = time,
        updated_at = time,
       
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

def authenticate_user(email: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_service(db:Session, id):

    user = db.query(User).filter(User.id == id).first()
    return user

# def get_this_user_service(db:Session, id):

#     user = db.query(User).filter(User.id == id).first()
#     return user

def update_user_self_service(db:Session,id,payload:UserUpdateSelf):

    user = db.query(User).filter(User.id == id).first()

    if not user:
        return None

    for field, value in payload.dict().items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

def update_user_admin_service(db:Session,id,payload:UserUpdateAdmin):

    user = db.query(User).filter(User.id == id).first()

    if not user:
        return None

    for field, value in payload.dict().items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user_service(db:Session,id):
    user = db.query(User).filter(User.id == id).first()

    db.delete(user)
    db.commit()

    return True

