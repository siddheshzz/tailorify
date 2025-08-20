from fastapi import FastAPI
from app.api.v1.endpoints import auth, booking, service
from app.db.base import Base
from app.db.session import engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

app.include_router(service.router, prefix="/api/v1/service", tags=["Service"])
app.include_router(booking.router, prefix="/api/v1/booking", tags=["Booking"])

@app.get("/")
def read_root():
    return {"message": "Tailor Backend Running"}
