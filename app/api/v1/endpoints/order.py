from uuid import UUID
from app.core.dependencies import OrderServiceDep
from app.core.exceptions import DuplicateResourceError, InternalDatabaseError
from app.core.s3_api import generate_download_url, generate_presigned_upload_url
from app.core.security import JWTBearer, decode_access_token,RoleChecker, get_current_user
from app.models.order_image import OrderImage
from app.schemas.order_image import OrderImageResponse
from app.schemas.s3 import UploadUrlSchemaOut
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
from app.schemas.order import OrderCreate, OrderResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.image_service import upload_order_image
from app.schemas.order_image import OrderImageResponse,ImageUploadConfirmation
from app.services.s3_service import S3Service



allow_admin = RoleChecker(["admin"])

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=OrderResponse,dependencies=[Depends(JWTBearer())])
async def create_order(order: OrderCreate, service: OrderServiceDep):
    try:
        return await service.add(order)
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
async def list_order(service :OrderServiceDep):
    return await service.get()

@router.get("/me", response_model=List[OrderResponse],dependencies=[Depends(JWTBearer())])
async def list_order_me(service:OrderServiceDep,current_user = Depends(get_current_user)):
    return await service.getMe(UUID(current_user.id))

@router.get("/me/{order_id}", response_model=OrderResponse | None,dependencies=[Depends(JWTBearer())])
async def get_order_me(order_id: UUID,service :OrderServiceDep,current_user = Depends(get_current_user)):
    order = await service.getMeId(UUID(current_user.id), order_id)

    if order is None:
        # Raise a 404 error if the resource doesn't exist or doesn't belong to the client
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found for current user."
        )
        
    return order

@router.get("/{order_id}", response_model=OrderResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
async def get_order(order_id, service: OrderServiceDep):
    order = await service.getId(UUID(order_id))

    if order is None:
        # Raise 404 if not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found."
        )
    return order

@router.put("/{order_id}", response_model=OrderResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
async def update_order(order_id:UUID,payload : OrderCreate,service:OrderServiceDep):
    # updated = update_order_service(db,order_id,payload)

    # if not updated:
    #     raise HTTPException(status_code=404, detail="Order not found")
    
    try:
        updated_order = await service.update(order_id,payload) 
        # updated_order = update_order_service(db, order_id, payload)

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

# @router.post("/{order_id}/images", response_model=OrderImageResponse)
# async def upload_image(order_id:UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    
#     # Check order exists
#     order = get_order(db,order_id)
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")

#     # Upload image
#     saved_image = upload_order_image(db, order_id, file, order)
#     return saved_image


@router.delete("/{order_id}", status_code=204,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
async def delete_order(order_id:UUID,service:OrderServiceDep):
    try:
        deleted = await service.remove(order_id) 

        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with ID {order_id} not found.")
        
        return
    
    except InternalDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred during order deletion."
        )







@router.get("/{order_id}/generate-upload-url")
async def get_upload_image(order_id:UUID,service:OrderServiceDep, file_extension: Optional[str] = None,content_type: Optional[str] = "image/jpeg", current_user = Depends(get_current_user)):
    
    # Check order exists
    # order = get_order_by_id(order_id,db)
    order = await service.getId(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    url_data = await generate_presigned_upload_url()

    return url_data

# @router.get("/{order_id}/generate-download-url")
# async def get_download_image(order_id,service:OrderServiceDep, file_extension: Optional[str] = None,content_type: Optional[str] = "image/jpeg", current_user = Depends(get_current_user)):
    
#     # Check order exists
#     order = get_order_by_id(order_id,db)
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
    
#     if order.client_id != UUID(current_user.id):
#         raise HTTPException(status_code=404, detail="Not your order")
    
#     images = db.query(OrderImage).filter(OrderImage.order_id == UUID(order_id)).all()
    
    
#     download_link = await generate_download_url(images.s3_url) 
#     return download_link




@router.post("/{order_id}/confirm-upload")
async def confirm_image_upload(
    order_id: UUID,
    service: OrderServiceDep,
    payload: ImageUploadConfirmation,
    current_user = Depends(get_current_user)
):
    # Verify order exists and belongs to user
    order = await service.getId(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # if order.client_id != UUID(current_user.id):
    #     raise HTTPException(status_code=403, detail="Not your order")
    
    # Save the image record to database
    # You'll need to create this service function
    from app.services.image_service import save_order_image_record
    
    # saved_image = save_order_image_record(
    #     db=db,
    #     order_id=order_id,
    #     s3_object_path=payload.s3_object_path,
    #     uploaded_by=payload.uploaded_by
    # )

    saved_image = await save_order_image_record(
        service,
        order_id=str(order_id),
        s3_object_path=payload.s3_object_path,
        uploaded_by=str(payload.uploaded_by),
        image_type=payload.image_type 
    )

    # update = update_order_service_with_image(db, UUID(order_id), payload)

    
    return saved_image
@router.get("/{order_id}/images", response_model=List[OrderImageResponse])
async def get_order_images(
    order_id: str,
    service: OrderServiceDep,
    current_user = Depends(get_current_user)
):
    """Get all images for an order"""
    from app.models.order_image import OrderImage
    from uuid import UUID
    
    # Verify order exists
    order = await service.getId(UUID(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get all images for this order
    images = await service.getImages(UUID(order_id))



    # Refresh download URLs (they expire after 6 hours)
    image: OrderImage
    for image in images:
        path = getattr(image, "s3_object_path")
        fresh_url_response = await generate_download_url(path)
        setattr(image, "s3_url", fresh_url_response.download_link)
        # path_str = str(image.s3_object_path)


    

    return images