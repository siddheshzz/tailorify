from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app/db_data/app.db")

# sqlite:///./app.db
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    print("&*&*&*&*&*&*&*&*&*&*&*&*&&*&*&*&*&*&*&*&*&*&*&*&*&")
    print("&*&*&*&*&*&*&*&*&*&*&*&*&&*&*&*&*&*&*&*&*&*&*&*&*&")
    print("&*&*&*&*&*&*&*&*&*&*&*&*&&*&*&*&*&*&*&*&*&*&*&*&*&")
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, connect_args=connect_args,echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()