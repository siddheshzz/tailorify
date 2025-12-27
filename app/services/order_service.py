import logging
import os
import shutil
import tempfile
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as app_config
from app.core.exceptions import DatabaseCommunicationError, OrderNotFoundError


from app.models.order import Order
from app.models.order_image import OrderImage
from app.schemas.order import OrderCreate
from app.services.storage.factory import get_storage_service

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, session: AsyncSession):
        # Get database session to perform database operations
        self.session = session

    async def get(self):
        services = await self.session.execute(select(Order))
        return services.scalars().all()

    async def getId(self, id):
        result = await self.session.execute(select(Order).filter(Order.id == id))
        service = result.scalar()
        return service

    async def getMe(self, client_id):
        service = await self.session.execute(
            select(Order).filter(Order.client_id == client_id)
        )
        return service.scalars().all()

    async def getMeId(self, client_id, order_id):
        try:
            result = await self.session.execute(
                select(Order)
                .filter(Order.client_id == client_id)
                .filter(Order.id == order_id)
            )
            order = result.scalar_one_or_none()

            if not order:
                raise OrderNotFoundError(f"Order {order_id} not found for this client.")

            return order
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching order {order_id}: {str(e)}")
            # Don't leak raw DB errors to the user; wrap them in a custom exception
            raise DatabaseCommunicationError(
                "An internal error occurred while fetching the record."
            )

    async def add(self, order) -> Order:
        ser = Order(**order.model_dump())

        self.session.add(ser)

        await self.session.commit()
        await self.session.refresh(ser)

        return ser

    async def addOrderImage(self, orderImage: OrderImage) -> OrderImage:
        self.session.add(orderImage)

        await self.session.commit()
        await self.session.refresh(orderImage)

        return orderImage

    async def remove(self, id):
        result = await self.session.execute(select(Order).filter(Order.id == id))

        service = result.scalar_one_or_none()
        if not service:
            return False
        await self.session.delete(service)
        await self.session.commit()

        return True

    async def update(self, id, payload: OrderCreate):
        res = await self.getId(id)

        if res is None:
            return None

        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(res, field, value)

        await self.session.commit()
        await self.session.refresh(res)

        return res

    async def updateOrderImage(self, orderImage):
        ser = await self.addOrderImage(orderImage)

        await self.session.commit()
        await self.session.refresh(ser)
        # db.query(OrderImage).filter(OrderImage.order_id == UUID(order_id)).all()

    async def getImageImageId(self, image_id):
   
        try:
            res = await self.session.execute(
                select(OrderImage).filter(OrderImage.id == UUID(image_id))
            )
        except Exception as e:
        
            await self.session.rollback()
            raise Exception(f"Failed to upload image: {str(e)}")

        image = res.scalar_one_or_none()

        return image

    async def getOrderImages(self, order_id):

        res = await self.session.execute(
            select(OrderImage).filter(OrderImage.order_id == order_id)
        )
        return list(res.scalars().all())

    async def getOrderImagesAll(self):
        res = await self.session.execute(select(OrderImage))
        return list(res.scalars().all())

    async def save_order_image_record(
        self,
        order_id: str,
        s3_object_path: str,
        s3_url: str,
        uploaded_by: str,
        image_type: str = "before",
    ) -> OrderImage:
        # Create new image record
        db_image = OrderImage(
            id=uuid4(),
            order_id=UUID(order_id),
            uploaded_by=UUID(uploaded_by),
            s3_url=s3_url,  # Store the download URL
            s3_object_path=s3_object_path,
            image_type=image_type,
            uploaded_at=datetime.now(timezone.utc),
        )
        self.session.add(db_image)
        await self.session.commit()
        await self.session.refresh(db_image)
        return db_image

    async def upload_order_image_to_storage(
        self, order_id: str, file: UploadFile, uploaded_by: str, image_type: str
    ) -> OrderImage:
        """
        Upload image file to storage (MinIO or S3).
        Works with both local and production environments.
        """

        storage_service = get_storage_service()
        temp_file_path = None

        try:
            # print(f"📸 Starting upload for order {order_id}")
            # print(f"   File: {file.filename}")
            # print(f"   Type: {file.content_type}")
            # print(f"   Image Type: {image_type}")
            # Validate file type
            if file.content_type not in app_config.ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed: {', '.join(app_config.ALLOWED_IMAGE_TYPES)}",
                )

            # Create temporary file
            file_extension = (
                os.path.splitext(file.filename)[1] if file.filename else ".jpeg"
            )
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
            temp_file_path = temp_file.name
            temp_file.close()

            # print(f"💾 Saving to temp file: {temp_file_path}")

            # Save uploaded file to temp location
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                buffer.flush()  # Explicitly push data to disk
                os.fsync(buffer.fileno())  # Ensure it's written

            # Verify file was saved
            file_size = os.path.getsize(temp_file_path)
            # print(f"✅ Temp file saved: {file_size} bytes")

            if file_size == 0:
                raise Exception("Uploaded file is empty")

            # Upload to storage
            # print("📤 Uploading to storage...")

            # Upload to storage (MinIO or S3)
            object_name = storage_service.upload_file(temp_file_path)
            # print(f"✅ Uploaded to storage: {object_name}")

            # Verify upload
            if not storage_service.file_exists(object_name):
                raise Exception(f"Upload verification failed for {object_name}")

            # Generate download URL
            # print("🔗 Generating download URL...")

            # Generate download URL
            download_url = storage_service.generate_presigned_download_url(
                object_name, expiry_minutes=app_config.PRESIGNED_URL_EXPIRY_MINUTES
            )
            # print("✅ Download URL generated")

            # Save to database
            db_image = OrderImage(
                id=uuid4(),
                order_id=UUID(order_id),
                uploaded_by=UUID(uploaded_by),
                s3_object_path=object_name,
                s3_url=download_url,
                image_type=image_type,
            )

            self.session.add(db_image)

            await self.session.commit()
            await self.session.refresh(db_image)

            return db_image

        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to upload image: {str(e)}")

        finally:
            # Step 6: Clean up temp file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    print("🗑️ Cleaned up temp file")
                except Exception as e:
                    print(f"Failed to delete temp file: {e}")

    async def delete_order_image(self, image_id: str) -> bool:
        """Delete image from storage and database"""
        storage_service = get_storage_service()
        print("*********")
        print("in delete order imageservice SERVICE")

        try:
            # Get image from database
            image = await self.getImageImageId(image_id)
            if not image:
                return False
            # Delete from storage
            storage_service.delete_file(image.s3_object_path)

            # Delete from database

            await self.session.delete(image)
            await self.session.commit()

            return True
        except Exception as e:
            print(f"Failed to delete image: {e}")
            return False

    async def regenerate_download_urls(
        self, images: list[OrderImage]
    ) -> list[OrderImage]:
        """Regenerate fresh download URLs for a list of images"""
        storage_service = get_storage_service()

        for image in images:
            try:
                fresh_url = storage_service.generate_presigned_download_url(
                    image.s3_object_path,
                    expiry_minutes=app_config.PRESIGNED_URL_EXPIRY_MINUTES,
                )
                image.s3_url = fresh_url
            except Exception as e:
                print(f"Failed to regenerate URL for {image.s3_object_path}: {e}")

        return images

    # async def download_file(self, images: list[OrderImage]) -> str:
    #     """Regenerate fresh download URLs for a list of images"""
    #     storage_service = get_storage_service()

    #     for image in images:
    #         try:
    #             fresh_url = storage_service.generate_presigned_download_url(
    #                 image.s3_object_path,
    #                 expiry_minutes=app_config.PRESIGNED_URL_EXPIRY_MINUTES,
    #             )
    #             image.s3_url = fresh_url
    #         except Exception as e:
    #             print(f"Failed to regenerate URL for {image.s3_object_path}: {e}")



    #     name = images[0].s3_object_path.rsplit("/", 1)[-1]
    #     path = images[0].s3_object_path
    #     res = storage_service.download_file(name, path)

    #     return res



