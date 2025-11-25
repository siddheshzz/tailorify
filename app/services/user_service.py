from app.models.user import User
from app.db.session import SessionLocal
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import datetime

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
