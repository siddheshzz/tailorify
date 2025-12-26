from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import HTTPBearer

from app.core.dependencies import OrderServiceDep
from app.core.exceptions import DuplicateResourceError, InternalDatabaseError
from app.core.security import RoleChecker, get_current_user
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.order_image import OrderImageResponse
from app.schemas.user import UserAuthPayload
from app.services.image_service import (
    regenerate_download_urls,
)

allow_admin = RoleChecker(["admin"])

router = APIRouter()
security = HTTPBearer()


@router.post("/", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    service: OrderServiceDep,
    current_user: UserAuthPayload = Depends(get_current_user),
):
    try:
        return await service.add(order)
    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InternalDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred during order creation.",
        )


@router.get(
    "/", response_model=List[OrderResponse], dependencies=[Depends(allow_admin)]
)
async def list_order(
    service: OrderServiceDep, current_user: UserAuthPayload = Depends(get_current_user)
):
    return await service.get()


@router.get("/me", response_model=List[OrderResponse])
async def list_order_me(
    service: OrderServiceDep, current_user=Depends(get_current_user)
):
    return await service.getMe(UUID(current_user.id))


@router.get("/me/{order_id}", response_model=OrderResponse | None)
async def get_order_me(
    order_id: UUID, service: OrderServiceDep, current_user=Depends(get_current_user)
):
    order = await service.getMeId(UUID(current_user.id), order_id)

    if order is None:
        # Raise a 404 error if the resource doesn't exist or doesn't belong to the client
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found for current user.",
        )

    return order


@router.get(
    "/{order_id}", response_model=OrderResponse, dependencies=[Depends(allow_admin)]
)
async def get_order(
    order_id,
    service: OrderServiceDep,
    current_user: UserAuthPayload = Depends(get_current_user),
):
    order = await service.getId(UUID(order_id))

    if order is None:
        # Raise 404 if not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found.",
        )
    return order


@router.put(
    "/{order_id}", response_model=OrderResponse, dependencies=[Depends(allow_admin)]
)
async def update_order(
    order_id: UUID,
    payload: OrderCreate,
    service: OrderServiceDep,
    current_user: UserAuthPayload = Depends(get_current_user),
):

    try:
        updated_order = await service.update(order_id, payload)
        # updated_order = update_order_service(db, order_id, payload)

        if updated_order is None:
            # Service function returns None if the order ID wasn't found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found.",
            )

        return updated_order

    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InternalDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred during order update.",
        )


@router.delete("/{order_id}", status_code=204, dependencies=[Depends(allow_admin)])
async def delete_order(
    order_id: UUID,
    service: OrderServiceDep,
    current_user: UserAuthPayload = Depends(get_current_user),
):
    try:
        deleted = await service.remove(order_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found.",
            )

        return

    except InternalDatabaseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred during order deletion.",
        )





@router.post("/{order_id}/upload-image", response_model=OrderImageResponse)
async def upload_order_image_endpoint(
    order_id: str,
    service: OrderServiceDep,
    file: UploadFile = File(...),
    image_type: str = Form("before"),
    current_user=Depends(get_current_user),
):
    """
    Upload image for an order (Client only - their own orders).
    Works with both MinIO and AWS S3.
    """
    # Verify order exists and belongs to user
    order = await service.getId(UUID(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.client_id != UUID(current_user.id):
        raise HTTPException(status_code=403, detail="Not your order")

    # Validate image_type
    valid_types = ["before", "after", "reference", "instruction"]
    if image_type not in valid_types:
        raise HTTPException(
            status_code=400, detail=f"Invalid image_type. Must be one of: {valid_types}"
        )

    try:
        saved_image = await service.upload_order_image_to_storage(
            order_id=order_id,
            file=file,
            uploaded_by=current_user.id,
            image_type=image_type,
        )
        return saved_image
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post(
    "/{order_id}/admin-upload-image",
    response_model=OrderImageResponse,
    dependencies=[Depends(allow_admin)],
)
async def admin_upload_order_image(
    order_id: str,
    service: OrderServiceDep,
    file: UploadFile = File(...),
    image_type: str = Form("before"),
    current_user=Depends(get_current_user),
):
    """
    Upload image for any order (Admin only).
    Works with both MinIO and AWS S3.
    """
    # Verify order exists
    order = await service.getId(UUID(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Validate image_type
    valid_types = ["before", "after", "reference", "instruction"]
    if image_type not in valid_types:
        raise HTTPException(
            status_code=400, detail=f"Invalid image_type. Must be one of: {valid_types}"
        )

    try:
        saved_image = await service.upload_order_image_to_storage(
            order_id=order_id,
            file=file,
            uploaded_by=current_user.id,
            image_type=image_type,
        )
        return saved_image
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{order_id}/images", response_model=List[OrderImageResponse])
async def get_order_images(
    order_id: str, service: OrderServiceDep, current_user=Depends(get_current_user)
):
    """
    Get all images for an order with fresh download URLs.
    Accessible by order owner or admin.
    """
    # Verify order exists
    order = await service.getId(UUID(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check access (owner or admin)
    if order.client_id != UUID(current_user.id) and current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Access denied")


    images = await service.getOrderImages(order_id)

    # Regenerate fresh download URLs
    images = await service.regenerate_download_urls(images)

    return images


@router.delete("/images/{image_id}", status_code=204)
async def delete_order_image_endpoint(
    image_id: str, service: OrderServiceDep, current_user=Depends(get_current_user)
):
    """
    Delete an image (Client can delete their own, Admin can delete any).
    Deletes from both storage and database.
    """
    # Get image
    print("IIN DELETE IMAGE")
    image = await service.getImageImageId(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Get order to check ownership
    print("IIN DELETE order")
    # order = service.getOrderImages(image.order_id)

    # Check permissions
    # is_owner = image.uploaded_by is UUID(current_user.id)
    is_owner = False
    is_admin = current_user.user_type == "admin"

    print(is_admin)
    print(is_owner)

    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete image
    success = await service.delete_order_image(image_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete image")

    return None


@router.get(
    "/admin/all-images",
    response_model=List[OrderImageResponse],
    dependencies=[Depends(allow_admin)],
)
async def get_all_order_images(
    service: OrderServiceDep,
    skip: int = 0,
    limit: int = 100,
):
    """Get all images across all orders (Admin only)"""
    images = await service.getOrderImagesAll()
    images = await regenerate_download_urls(images)
    return images
