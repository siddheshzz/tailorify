# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


# DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app/db_data/app.db")

DATABASE_URL = os.environ.get("DATABASE_URL")

# sqlite:///./app.db
# connect_args = {}
# if DATABASE_URL.startswith("sqlite"):
#     connect_args = {"check_same_thread": False}

# engine = create_engine(
#     DATABASE_URL, connect_args=connect_args,echo=True
# )
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine = create_async_engine(DATABASE_URL, echo=True)

async def create_db_tables():
    async with engine.begin() as connection:

        # from models.user import User
        # from models.order import Order
        # from models.service import Service
        # from models.order_image import OrderImage
        # from models.booking import Booking
        await connection.run_sync(SQLModel.metadata.create_all)

# AsyncSessionLocal = sessionmaker(
#     engine, class_=AsyncSession, expire_on_commit=False
# )

async def get_session():
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


def get_db():
    pass

# def get_db():
#     db = AsyncSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# Dependency for routes
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session


