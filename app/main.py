from fastapi import FastAPI
from app.api.v1.endpoints import auth
from app.db.base import Base
from app.db.session import engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

@app.get("/")
def read_root():
    return {"message": "Tailor Backend Running"}
