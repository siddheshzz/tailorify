from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.endpoints import auth, booking, service, order, user, order_image
from app.models.base import Base
from fastapi.middleware.cors import CORSMiddleware
import app.models
from app.db.session import create_db_tables, engine

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_tables()
    yield

    
app = FastAPI(lifespan=lifespan_handler)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])


app.include_router(service.router, prefix="/api/v1/service", tags=["Service"])
app.include_router(order.router, prefix="/api/v1/order", tags=["Order"])
app.include_router(order_image.router, prefix="/api/v1/order", tags=["Order_image"])
app.include_router(booking.router, prefix="/api/v1/booking", tags=["Booking"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])


@app.get("/")
def read_root():
    return {"message": "Tailor Backend Running"}
