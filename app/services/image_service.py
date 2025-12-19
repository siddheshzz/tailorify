# services/image_service.py
from datetime import datetime
from uuid import UUID, uuid4
from app.core.dependencies import OrderServiceDep
from app.core.s3_api import generate_download_url
from app.schemas.order import OrderCreate
from sqlalchemy.orm import Session
from app.models.order_image import OrderImage
from app.core.file_utils import save_order_image

def upload_order_image(db: Session, order_id, file,order:OrderCreate):
    # Save file
    file_path, file_name = save_order_image(order_id, file)

    # Save DB record
    db_image = OrderImage(
        order_id=order_id,
        s3_url=file_path,
        uploaded_by=order.client_id,
        image_type="before"

    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return db_image

async def save_order_image_record(service:OrderServiceDep, 
    order_id: str, 
    s3_object_path: str,
    uploaded_by: str,
    image_type: str = "before")->OrderImage:


    download_url_response = await generate_download_url(s3_object_path)
    s3_url = download_url_response.download_link
    
    
    # db_image = OrderImage(
    #     order_id=order_id,
    #     s3_url=s3_object_path,
    #     image_type="before",
    #     uploaded_by=uploaded_by
        
    # )

    # Create new image record
    db_image = OrderImage(
        id=uuid4(),
        order_id=UUID(order_id),
        uploaded_by=UUID(uploaded_by),
        s3_url=s3_url,  # Store the download URL
        s3_object_path=s3_object_path,
        image_type=image_type,
        uploaded_at=datetime.utcnow(),
    )

    result = await service.updateOrderImage(db_image)

    return db_image
