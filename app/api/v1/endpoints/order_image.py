# api/v1/order_images.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.db.session import get_db
# from app.services.image_service import upload_order_image
# from app.models.order import Order
# from app.schemas.order_image import OrderImageResponse

# router = APIRouter()

# @router.post("/{order_id}/images", response_model=OrderImageResponse)
# def upload_image(order_id, file: UploadFile = File(...), db: Session = Depends(get_db)):
    
#     # Check order exists
#     order = db.query(Order).filter(Order.id == order_id).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")

#     # Upload image
#     saved_image = upload_order_image(db, order_id, file, order)
#     return saved_image
