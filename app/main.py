from fastapi import FastAPI
from app.api.v1.endpoints import auth, booking, service, order, user
from app.models.base import Base
import app.models
from app.db.session import engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])


app.include_router(service.router, prefix="/api/v1/service", tags=["Service"])
app.include_router(order.router, prefix="/api/v1/order", tags=["Order"])
app.include_router(booking.router, prefix="/api/v1/booking", tags=["Booking"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])


@app.get("/")
def read_root():
    return {"message": "Tailor Backend Running"}
