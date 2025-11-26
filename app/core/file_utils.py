# utils/file_utils.py
import os
import uuid

MEDIA_ROOT = "media/orders"

def save_order_image(order_id, file) -> str:
    os.makedirs(f"{MEDIA_ROOT}/{order_id}", exist_ok=True)

    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    path = f"{MEDIA_ROOT}/{order_id}/{unique_name}"

    with open(path, "wb") as buffer:
        buffer.write(file.file.read())

    return path, unique_name
