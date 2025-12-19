from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import DatabaseCommunicationError, OrderNotFoundError
from app.core.s3_api import generate_download_url
from app.models.order import Order
from app.models.order_image import OrderImage
from app.schemas.order import OrderCreate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging


logger = logging.getLogger(__name__)



class OrderService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    async def get(self):
        services = await self.session.execute(select(Order))
        return services.scalars().all()
    
    async def getId(self,id):
        result = await self.session.execute(select(Order).filter(Order.id == id))
        service = result.scalar()
        return service
        
    async def getMe(self,client_id):
        service = await self.session.execute(select(Order).filter(Order.client_id == client_id))
        return service.scalars().all()
    
    async def getMeId(self,client_id,order_id):
        try:
            result = await self.session.execute(select(Order).filter(Order.client_id == client_id).filter(Order.id == order_id))
            order = result.scalar_one_or_none()

            if not order:
                raise OrderNotFoundError(f"Order {order_id} not found for this client.")
        
            return order
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching order {order_id}: {str(e)}")
            # Don't leak raw DB errors to the user; wrap them in a custom exception
            raise DatabaseCommunicationError("An internal error occurred while fetching the record.")


    async def add(self,order)-> Order:
        ser = Order(**order.model_dump())

        self.session.add(ser)

        await self.session.commit()
        await self.session.refresh(ser)

        return ser
    
    async def addOrderImage(self,orderImage:OrderImage)-> OrderImage:
        

        self.session.add(orderImage)

        await self.session.commit()
        await self.session.refresh(orderImage)

        return orderImage
    

    async def remove(self,id):
        result = await self.session.execute(select(Order).filter(Order.id == id))
        
        service = result.scalar_one_or_none()
        if not service:
            return False
        await self.session.delete(service)
        await self.session.commit()

        return True
    
    async def update(self, id,payload:OrderCreate):
        res = await self.getId(id)

        if res is None:
            return None
        
        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(res,field,value)

        await self.session.commit()
        await self.session.refresh(res)

        return res
    
    async def updateOrderImage(self,orderImage):
        ser = await self.addOrderImage(orderImage)

        await self.session.commit()
        await self.session.refresh(ser)
        # db.query(OrderImage).filter(OrderImage.order_id == UUID(order_id)).all()

    async def getImages(self, order_id):
        # res = await self.session.execute(select(OrderImage).filter(OrderImage.order_id == order_id))

        # images = res.scalars().all()

        # for image in images:
        #     path = image.s3_object_path
        #     fresh_url_response = await generate_download_url(path)
        #     image.s3_url = fresh_url_response.download_link

        res = await self.session.execute(
        select(OrderImage).filter(OrderImage.order_id == order_id)
        )
        return list(res.scalars().all())
        

        # return images



    



# def create_order_service(db: Session, order: OrderCreate):
#     db_order = Order(**order.dict())
#     db.add(db_order)
#     db.commit()
#     db.refresh(db_order)
#     return db_order

# def get_orders(db: Session, skip: int = 0, limit: int = 10):
#     return db.query(Order).offset(skip).limit(limit).all()


# def get_orders_me(db: Session,current_id, skip: int = 0, limit: int = 10):
#     return db.query(Order).filter(Order.client_id == current_id).offset(skip).limit(limit).all()

# def get_order_by_id_me(order_id:UUID , db: Session, current_id):
#     try:
#         order = db.query(Order).filter(Order.id == order_id).filter(Order.client_id==UUID(current_id)).first()
#         return order
#     except IntegrityError as e:
#         logger.warning(f"Integrity error when creating service: {e}")
#         # raise DuplicateResourceError("Service with this name/detail already exists.")
#     except SQLAlchemyError as e:
#         # db.rollback() # Rollback for any other DB error
#         logger.error(f"Database error during service creation: {e}")
#         # Raise a generic DB error that the API layer will handle

# def get_order_by_id(order_id:UUID , db: Session):
#     order = db.query(Order).filter(Order.id == order_id).first()

#     return order


# def update_order_service(db:Session,order_id:UUID, payload:OrderCreate):
#     order = db.query(Order).filter(Order.id == order_id).first()

#     if not order:
#         return None

#     for field, value in payload.dict().items():
#         setattr(order, field, value)

#     db.commit()
#     db.refresh(order)
#     return order

# def order_image(db:Session,order_id):
#      # Check order exists
#     order = db.query(Order).filter(Order.id == order_id).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")

#     # Upload image
#     saved_image = upload_order_image(db, order_id, file, order)
#     return saved_image


# def delete_order_service( db:Session,order_id: UUID,):
#     order = db.query(Order).filter(Order.id == order_id).first()

#     db.delete(order)
#     db.commit()

#     return True

