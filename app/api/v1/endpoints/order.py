from uuid import UUID
from app.core.exceptions import DuplicateResourceError, InternalDatabaseError
from app.core.s3_api import generate_presigned_upload_url
from app.core.security import JWTBearer, decode_access_token,RoleChecker, get_current_user
from app.schemas.order_image import OrderImageResponse
from app.schemas.s3 import UploadUrlSchemaOut
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import create_order_service, get_order_by_id_me, get_orders, get_order_by_id, get_orders_me, update_order_service,delete_order_service
from app.db.session import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.image_service import upload_order_image
from app.schemas.order_image import OrderImageResponse,ImageUploadConfirmation



allow_admin = RoleChecker(["admin"])

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=OrderResponse,dependencies=[Depends(JWTBearer())])
def create_order(service: OrderCreate, db: Session = Depends(get_db)):
    # return create_order_service(db, service)
    try:
        # Pass current_user.id to the service layer for client_id
        return create_order_service(db, service)
    except DuplicateResourceError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except InternalDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred during order creation."
        )


@router.get("/", response_model=List[OrderResponse],dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
def list_order(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_orders(db, skip, limit)

@router.get("/me", response_model=List[OrderResponse],dependencies=[Depends(JWTBearer())])
def list_order_me(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    return get_orders_me(db,current_user.id, skip, limit)

@router.get("/me/{order_id}", response_model=OrderResponse,dependencies=[Depends(JWTBearer())])
def get_order_me(order_id, db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    order = get_order_by_id_me(order_id, db, current_user.id)

    if order is None:
        # Raise a 404 error if the resource doesn't exist or doesn't belong to the client
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found for current user."
        )
        
    return order

@router.get("/{order_id}", response_model=OrderResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
def get_order(order_id, db: Session = Depends(get_db)):
    order = get_order_by_id(order_id,db)

    if order is None:
        # Raise 404 if not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )
    return order

@router.put("/{order_id}", response_model=OrderResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
def update_order(order_id,payload : OrderCreate, db: Session = Depends(get_db)):
    # updated = update_order_service(db,order_id,payload)

    # if not updated:
    #     raise HTTPException(status_code=404, detail="Order not found")
    
    try:
        updated_order = update_order_service(db, order_id, payload)

        if updated_order is None:
            # Service function returns None if the order ID wasn't found
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with ID {order_id} not found.")
        
        return updated_order
    
    except DuplicateResourceError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except InternalDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred during order update."
        )

@router.post("/{order_id}/images", response_model=OrderImageResponse)
def upload_image(order_id, file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    # Check order exists
    order = get_order(db,order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Upload image
    saved_image = upload_order_image(db, order_id, file, order)
    return saved_image


@router.delete("/{order_id}", status_code=204,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
def delete_order(order_id,db: Session = Depends(get_db)):
    # deleted = delete_user_service(db,order_id)

    # if not deleted:
    #     raise HTTPException(status_code=404, detail="Order not found")
    
    # return
    try:
        # NOTE: I assumed you meant 'delete_order_service', not 'delete_user_service'
        deleted = delete_order_service(db, order_id) 

        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with ID {order_id} not found.")
        
        # 204 No Content success response (returns no body)
        return
    
    except InternalDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred during order deletion."
        )







@router.get("/{order_id}/generate-upload-url")
async def get_upload_image(order_id, file_extension: Optional[str] = None,content_type: Optional[str] = "image/jpeg", db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    
    # Check order exists
    order = get_order_by_id(order_id,db)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.client_id != UUID(current_user.id):
        raise HTTPException(status_code=404, detail="Not your order")
    
    
    url_data = await generate_presigned_upload_url()

    return url_data




# @router.post("/{order_id}/generate-upload-url", response_model=OrderImageResponse)
# def upload_final_post_image(order_id,payload: dict,db: Session = Depends(get_db)):
#     pass


# @router.post("/{order_id}/confirm-upload")
# def confirm_image_upload(
#     order_id: str,
#     payload: ImageUploadConfirmation,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user)
# ):
#     # Verify order exists and belongs to user
#     order = get_order_by_id(db, order_id)
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
    
#     if order.client_id != UUID(current_user.user_id):
#         raise HTTPException(status_code=403, detail="Not your order")
    
#     # Save the image record to database
#     # You'll need to create this service function
#     from app.services.image_service import save_order_image_record
    
#     saved_image = save_order_image_record(
#         db=db,
#         order_id=order_id,
#         s3_object_path=payload.s3_object_path
#     )
    
#     return saved_image