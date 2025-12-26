# services/image_service.py
import os
import shutil
import tempfile
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings as app_config
from app.core.file_utils import save_order_image
from app.models.order_image import OrderImage

# from app.core.s3_api import generate_download_url
from app.schemas.order import OrderCreate
from app.services.storage.factory import get_storage_service


def upload_order_image(db: Session, order_id, file, order: OrderCreate):
    # Save file
    file_path, file_name = save_order_image(order_id, file)

    # Save DB record
    db_image = OrderImage(
        order_id=order_id,
        s3_url=file_path,
        uploaded_by=order.client_id,
        image_type="before",
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return db_image


# async def save_order_image_record(service:OrderServiceDep,
#     order_id: str,
#     s3_object_path: str,
#     uploaded_by: str,
#     image_type: str = "before")->OrderImage:


#     download_url_response = await generate_download_url(s3_object_path)
#     s3_url = download_url_response.download_link


#     # db_image = OrderImage(
#     #     order_id=order_id,
#     #     s3_url=s3_object_path,
#     #     image_type="before",
#     #     uploaded_by=uploaded_by

#     # )

#     # Create new image record
#     db_image = OrderImage(
#         id=uuid4(),
#         order_id=UUID(order_id),
#         uploaded_by=UUID(uploaded_by),
#         s3_url=s3_url,  # Store the download URL
#         s3_object_path=s3_object_path,
#         image_type=image_type,
#         uploaded_at=datetime.utcnow(),
#     )

#     result = await service.updateOrderImage(db_image)

#     return db_image


async def upload_order_image_to_storage(
    db: Session, order_id: str, file: UploadFile, uploaded_by: str, image_type: str
) -> OrderImage:
    """
    Upload image file to storage (MinIO or S3).
    Works with both local and production environments.
    """

    storage_service = get_storage_service()
    temp_file_path = None

    try:
        # Validate file type
        if file.content_type not in app_config.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(app_config.ALLOWED_IMAGE_TYPES)}",
            )

        # Step 1: Create temporary file
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file_path = temp_file.name

        # Step 2: Save uploaded file to temp location
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 3: Upload to storage (MinIO or S3)
        object_name = storage_service.upload_file(temp_file_path)

        # Step 4: Generate download URL
        download_url = storage_service.generate_presigned_download_url(
            object_name, expiry_minutes=app_config.PRESIGNED_URL_EXPIRY_MINUTES
        )

        # Step 5: Save to database
        db_image = OrderImage(
            id=uuid4(),
            order_id=UUID(order_id),
            uploaded_by=UUID(uploaded_by),
            s3_object_path=object_name,
            s3_url=download_url,
            image_type=image_type,
            uploaded_at=datetime.utcnow(),
        )

        db.add(db_image)
        db.commit()
        db.refresh(db_image)

        return db_image

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to upload image: {str(e)}")

    finally:
        # Step 6: Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Failed to delete temp file: {e}")


async def delete_order_image(db: Session, image_id: str) -> bool:
    """Delete image from storage and database"""
    storage_service = get_storage_service()

    try:
        # Get image from database
        image = db.query(OrderImage).filter(OrderImage.id == UUID(image_id)).first()
        if not image:
            return False

        # Delete from storage
        storage_service.delete_file(image.s3_object_path)

        # Delete from database
        db.delete(image)
        db.commit()

        return True
    except Exception as e:
        db.rollback()
        print(f"Failed to delete image: {e}")
        return False


async def regenerate_download_urls(images: list[OrderImage]) -> list[OrderImage]:
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
