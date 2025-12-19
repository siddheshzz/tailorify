from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.service import Service
from app.schemas.service import ServiceCreate
from sqlalchemy.ext.asyncio import AsyncSession


class ServiceService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    async def get(self):
        services = await self.session.execute(select(Service))
        return services.scalars().all()
    
    async def getId(self,id):
        service = await self.session.execute(select(Service).filter(Service.id == id))
        return service.scalar()

    async def add(self,service)-> Service:
        ser = Service(**service.model_dump())

        self.session.add(ser)

        await self.session.commit()
        await self.session.refresh(ser)

        return ser
    async def remove(self,id):
        result = await self.session.execute(select(Service).filter(Service.id == id))
        
        service = result.scalar_one_or_none()
        if not service:
            return False
        await self.session.delete(service)
        await self.session.commit()

        return True
    
    async def update(self, id,updateService):
        res = await self.getId(id)

        if res is None:
            return None
        
        data = updateService.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(res,field,value)

        await self.session.commit()
        await self.session.refresh(res)

        return res

        # stmt = (
        # update(Service)
        # .where(Service.id == id)
        # .values(**updateService.model_dump())
        # .execution_options(synchronize_session="fetch")
        # )

        # result = await self.session.execute(stmt)

