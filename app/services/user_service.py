from sqlalchemy import select
from app.models.user import User

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import datetime
from app.schemas.user import UserUpdateAdmin, UserUpdateSelf


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id):
        return await self.session.get(User, id)
    
    async def add(self,user_data) -> User:
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
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user
    async def authenticate_user(self, email,password):
        # stmt = select(User).where(User.email == email)
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar()
        print(user)
        print("xxxxxxxxxx")
        print("xxxxxxxxxx")
        print("xxxxxxxxxx")
        print("xxxxxxxxxx")
        print(password)
        if user is None or not verify_password(password,user.hashed_password):
            return None
        return user
    






# async def create_user(user_data,db:Session):
    
#     time = datetime.now()
#     user = User(
#         email=user_data.email,
#         hashed_password=get_password_hash(user_data.password),
#         first_name = user_data.first_name,
#         last_name = user_data.last_name,
#         user_type = 'client',
#         is_active = True,
#         created_at = time,
#         updated_at = time,
       
#     )
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     db.close()
#     return user

# def authenticate_user(email: str, password: str, db:AsyncSession):
#     stmt = select(User).where(User.email == email)
#     # user = db.query(User).filter(User.email == email).first()
#     user = db.exec(stmt).first()
#     db.close()
#     if not user or not verify_password(password, user.hashed_password):
#         return None
#     return user


def get_user_service(db:Session, id):

    user = db.query(User).filter(User.id == id).first()
    return user
def get_all_user_service(db:Session):
    users = db.query(User).all()
    return users
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

