from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from app.models.user import User

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import datetime
from app.schemas.user import  UserUpdateAdmin, UserUpdateSelf


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, user_id:UUID) -> Optional[User]:
        user = await self.session.get(User, user_id)
        
        return user
    
    async def getAll(self):
        users = await self.session.execute(select(User))
        return users.scalars().all()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def add(self,user_data) -> User:
        """Create a new user with a hashed password."""
        time = datetime.now()
        hashed_pw = get_password_hash(user_data.password)

        # 2. Convert Pydantic model to SQLAlchemy model
        # Exclude 'password' from the dict and add 'hashed_password'
        user_data = user_data.model_dump(exclude={"password"})
        db_user = User(**user_data, hashed_password=hashed_pw)

        # user = User(
        #     email=user_data.email,
        #     hashed_password=get_password_hash(user_data.password),
        #     first_name = user_data.first_name,
        #     last_name = user_data.last_name,
        #     user_type = 'client',
        #     is_active = True,
        #     created_at = time,
        #     updated_at = time,
        
        # )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user
    
    async def authenticate_user(self, email:str,password:str) -> Optional[User]:
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password,user.hashed_password):
            return None
        return user
    

    async def update_user_self_service(self,user_id:UUID,payload: UserUpdateSelf) -> Optional[User]:
        """Allow users to update their own basic info or password."""
        update_data = payload.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data['hashshed_password'] =get_password_hash(update_data.pop("password")) 
        # user = await self.get(user_id)


        query = (
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
            .returning(User)
        )
        
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().first()
    
    async def update_user_admin_service(self,user_id:UUID, payload:UserUpdateAdmin):
        update_data = payload.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data['hashshed_password'] =get_password_hash(update_data.pop("password"))

        query = (
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
            .returning(User)
        )
        
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalars().first()
        
    
    async def delete_user_service(self,id:UUID) -> bool:
        user = self.get(id)

        await self.session.delete(user)
        await self.session.commit()
        return True

    


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
# def get_all_user_service(db:Session):
#     users = db.query(User).all()
#     return users
# def get_this_user_service(db:Session, id):

#     user = db.query(User).filter(User.id == id).first()
#     return user

# def update_user_self_service(db:Session,id,payload:UserUpdateSelf):

#     user = db.query(User).filter(User.id == id).first()

#     if not user:
#         return None

#     for field, value in payload.dict().items():
#         setattr(user, field, value)

#     db.commit()
#     db.refresh(user)
#     return user

# def update_user_admin_service(db:Session,id,payload:UserUpdateAdmin):

#     user = db.query(User).filter(User.id == id).first()

#     if not user:
#         return None

#     for field, value in payload.dict().items():
#         setattr(user, field, value)

#     db.commit()
#     db.refresh(user)
#     return user


# def delete_user_service(db:Session,id):
#     user = db.query(User).filter(User.id == id).first()

#     db.delete(user)
#     db.commit()

#     return True

