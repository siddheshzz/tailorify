from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.booking_service import BookingService
from app.services.order_service import OrderService
from app.services.service import ServiceService
from app.services.user_service import UserService

# Asynchronous database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


def get_service(session: SessionDep) -> ServiceService:
    return ServiceService(session)


def get_order_service(session: SessionDep) -> OrderService:
    return OrderService(session)


def get_booking_service(session: SessionDep) -> BookingService:
    return BookingService(session)


# Shipment service dep annotation
UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]

ServiceServiceDep = Annotated[
    ServiceService,
    Depends(get_service),
]


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]

BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]
