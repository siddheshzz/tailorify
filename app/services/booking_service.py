from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.schemas.booking import BookingCreate


class BookingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, booking: BookingCreate, user_id: UUID):
        booking = Booking(
            **booking.model_dump(),
            user_id=user_id,
        )

        self.session.add(booking)
        await self.session.commit()
        await self.session.refresh(booking)

        return booking

    async def get_bookings_by_user(self, user_id: UUID):
        result = await self.session.execute(
            select(Booking).filter(Booking.user_id == user_id)
        )
        bookings = result.scalars().all()

        return bookings


