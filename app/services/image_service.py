# services/image_service.py
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

def save_order_image_record(db:Session, order_id,s3_object_path,uploaded_by):
    db_image = OrderImage(
        order_id=order_id,
        s3_url=s3_object_path,
        image_type="before",
        uploaded_by=uploaded_by
        
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)


    return db_image
