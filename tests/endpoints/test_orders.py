# """Order CRUD + image sub-resource endpoint tests."""

# import uuid
# from datetime import datetime, timezone
# from decimal import Decimal
# from types import SimpleNamespace

# from app.core.dependencies import get_order_service
# from app.core.security import get_current_user
# from app.main import app


# def _async(val):
#     async def _fn(*_a, **_kw):
#         return val

#     return _fn


# def _fake_order(order_id=None, client_id=None, status="pending"):
#     now = datetime.now(timezone.utc)
#     return SimpleNamespace(
#         id=order_id or uuid.uuid4(),
#         client_id=client_id or uuid.uuid4(),
#         service_id=uuid.uuid4(),
#         description="Test tailoring",
#         status=status,
#         priority="normal",
#         quoted_price=Decimal("99.99"),
#         actual_price=None,
#         requested_date=now,
#         estimated_completion=now,
#         actual_completion=None,
#         notes=None,
#         created_at=now,
#         updated_at=now,
#     )


# def _order_json(client_id=None, service_id=None):
#     return {
#         "client_id": str(client_id or uuid.uuid4()),
#         "service_id": str(service_id or uuid.uuid4()),
#         "quoted_price": "99.99",
#         "description": "Hemming",
#     }


# # ---------------------------------------------------------------------------
# # Create
# # ---------------------------------------------------------------------------
# class TestCreateOrder:
#     # def test_success(self, http_client, client_headers, client_payload):
#     #     order = _fake_order(client_id=uuid.UUID(client_payload.id))
#     #     app.dependency_overrides[get_current_user] = lambda: client_payload
#     #     app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#     #         add=_async(order)
#     #     )

#     #     res = http_client.post(
#     #         "/api/v1/order/",
#     #         json=_order_json(client_id=client_payload.id),
#     #         headers=client_headers,
#     #     )
#     #     assert res.status_code == 200
#     #     assert res.json()["status"] == "pending"

#     # def test_requires_auth(self, http_client):
#     #     res = http_client.post("/api/v1/order/", json={})
#     #     assert res.status_code == 403


# # ---------------------------------------------------------------------------
# # List
# # ---------------------------------------------------------------------------
# class TestListOrders:
#     def test_all_orders_admin_only(
#         self, http_client, admin_headers, admin_payload
#     ):
#         orders = [_fake_order(), _fake_order()]
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             get=_async(orders)
#         )

#         res = http_client.get("/api/v1/order/", headers=admin_headers)
#         assert res.status_code == 200
#         assert len(res.json()) == 2

#     def test_all_orders_rejects_client(
#         self, http_client, client_headers, client_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         res = http_client.get("/api/v1/order/", headers=client_headers)
#         assert res.status_code == 403

#     def test_my_orders(self, http_client, client_headers, client_payload):
#         orders = [_fake_order(client_id=uuid.UUID(client_payload.id))]
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getMe=_async(orders)
#         )

#         res = http_client.get("/api/v1/order/me", headers=client_headers)
#         assert res.status_code == 200
#         assert len(res.json()) == 1


# # ---------------------------------------------------------------------------
# # Get single order
# # ---------------------------------------------------------------------------
# class TestGetOrder:
#     def test_admin_get_by_id(self, http_client, admin_headers, admin_payload):
#         order = _fake_order()
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(order)
#         )

#         res = http_client.get(f"/api/v1/order/{order.id}", headers=admin_headers)
#         assert res.status_code == 200
#         assert res.json()["id"] == str(order.id)

#     def test_admin_get_404_when_missing(
#         self, http_client, admin_headers, admin_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(None)
#         )

#         res = http_client.get(
#             f"/api/v1/order/{uuid.uuid4()}", headers=admin_headers
#         )
#         assert res.status_code == 404

#     def test_my_order_by_id(self, http_client, client_headers, client_payload):
#         order = _fake_order(client_id=uuid.UUID(client_payload.id))
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getMeId=_async(order)
#         )

#         res = http_client.get(
#             f"/api/v1/order/me/{order.id}", headers=client_headers
#         )
#         assert res.status_code == 200

#     def test_my_order_404_when_not_owned(
#         self, http_client, client_headers, client_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getMeId=_async(None)
#         )

#         res = http_client.get(
#             f"/api/v1/order/me/{uuid.uuid4()}", headers=client_headers
#         )
#         assert res.status_code == 404


# # ---------------------------------------------------------------------------
# # Update
# # ---------------------------------------------------------------------------
# class TestUpdateOrder:
#     def test_admin_update_success(
#         self, http_client, admin_headers, admin_payload
#     ):
#         order = _fake_order(status="in_progress")
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             update=_async(order)
#         )

#         res = http_client.put(
#             f"/api/v1/order/{order.id}",
#             json=_order_json(
#                 client_id=order.client_id, service_id=order.service_id
#             ),
#             headers=admin_headers,
#         )
#         assert res.status_code == 200

#     def test_update_404_when_missing(
#         self, http_client, admin_headers, admin_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             update=_async(None)
#         )

#         res = http_client.put(
#             f"/api/v1/order/{uuid.uuid4()}",
#             json=_order_json(),
#             headers=admin_headers,
#         )
#         assert res.status_code == 404

#     def test_update_rejects_client(
#         self, http_client, client_headers, client_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         res = http_client.put(
#             f"/api/v1/order/{uuid.uuid4()}",
#             json=_order_json(),
#             headers=client_headers,
#         )
#         assert res.status_code == 403


# # ---------------------------------------------------------------------------
# # Delete
# # ---------------------------------------------------------------------------
# class TestDeleteOrder:
#     def test_admin_delete_success(
#         self, http_client, admin_headers, admin_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             remove=_async(True)
#         )

#         res = http_client.delete(
#             f"/api/v1/order/{uuid.uuid4()}", headers=admin_headers
#         )
#         assert res.status_code == 204

#     def test_delete_404_when_missing(
#         self, http_client, admin_headers, admin_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             remove=_async(False)
#         )

#         res = http_client.delete(
#             f"/api/v1/order/{uuid.uuid4()}", headers=admin_headers
#         )
#         assert res.status_code == 404

#     def test_delete_rejects_client(
#         self, http_client, client_headers, client_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         res = http_client.delete(
#             f"/api/v1/order/{uuid.uuid4()}", headers=client_headers
#         )
#         assert res.status_code == 403


# # ---------------------------------------------------------------------------
# # Order images sub-resource
# # ---------------------------------------------------------------------------
# class TestOrderImages:
#     def _image_ns(self, order_id, uploader_id):
#         return SimpleNamespace(
#             id=uuid.uuid4(),
#             order_id=order_id,
#             uploaded_by=uploader_id,
#             s3_object_path="orders/img.jpg",
#             s3_url="https://s3.example.com/img.jpg",
#             image_type="before",
#             uploaded_at=datetime.now(timezone.utc),
#         )

#     # -- list images --
#     def test_get_images_own_order(
#         self, http_client, client_headers, client_payload
#     ):
#         order = _fake_order(client_id=uuid.UUID(client_payload.id))
#         img = self._image_ns(order.id, uuid.UUID(client_payload.id))

#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(order),
#             getOrderImages=_async([img]),
#             regenerate_download_urls=_async([img]),
#         )

#         res = http_client.get(
#             f"/api/v1/order/{order.id}/images", headers=client_headers
#         )
#         assert res.status_code == 200
#         assert len(res.json()) == 1

#     def test_get_images_403_not_owner_not_admin(
#         self, http_client, client_headers, client_payload
#     ):
#         order = _fake_order(client_id=uuid.uuid4())  # different owner
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(order)
#         )

#         res = http_client.get(
#             f"/api/v1/order/{order.id}/images", headers=client_headers
#         )
#         assert res.status_code == 403

#     def test_get_images_admin_can_view_any(
#         self, http_client, admin_headers, admin_payload
#     ):
#         order = _fake_order()  # belongs to someone else
#         img = self._image_ns(order.id, order.client_id)

#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(order),
#             getOrderImages=_async([img]),
#             regenerate_download_urls=_async([img]),
#         )

#         res = http_client.get(
#             f"/api/v1/order/{order.id}/images", headers=admin_headers
#         )
#         assert res.status_code == 200

#     def test_get_images_404_order_missing(
#         self, http_client, client_headers, client_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(None)
#         )

#         res = http_client.get(
#             f"/api/v1/order/{uuid.uuid4()}/images", headers=client_headers
#         )
#         assert res.status_code == 404

#     # -- upload image --
#     def test_upload_rejects_non_owner(
#         self, http_client, client_headers, client_payload
#     ):
#         order = _fake_order(client_id=uuid.uuid4())  # not the current user
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(order)
#         )

#         res = http_client.post(
#             f"/api/v1/order/{order.id}/upload-image",
#             files={"file": ("test.jpg", b"imgdata", "image/jpeg")},
#             data={"image_type": "before"},
#             headers=client_headers,
#         )
#         assert res.status_code == 403

#     def test_upload_rejects_invalid_image_type_field(
#         self, http_client, client_headers, client_payload
#     ):
#         order = _fake_order(client_id=uuid.UUID(client_payload.id))
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(order)
#         )

#         res = http_client.post(
#             f"/api/v1/order/{order.id}/upload-image",
#             files={"file": ("test.jpg", b"imgdata", "image/jpeg")},
#             data={"image_type": "bogus"},  # not in valid_types
#             headers=client_headers,
#         )
#         assert res.status_code == 400

#     def test_upload_404_when_order_missing(
#         self, http_client, client_headers, client_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getId=_async(None)
#         )

#         res = http_client.post(
#             f"/api/v1/order/{uuid.uuid4()}/upload-image",
#             files={"file": ("test.jpg", b"imgdata", "image/jpeg")},
#             data={"image_type": "before"},
#             headers=client_headers,
#         )
#         assert res.status_code == 404

#     # -- delete image --
#     def test_delete_image_404_when_not_found(
#         self, http_client, admin_headers, admin_payload
#     ):
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getImageImageId=_async(None)
#         )

#         res = http_client.delete(
#             f"/api/v1/order/images/{uuid.uuid4()}", headers=admin_headers
#         )
#         assert res.status_code == 404

#     def test_delete_image_admin_success(
#         self, http_client, admin_headers, admin_payload
#     ):
#         image = SimpleNamespace(
#             id=uuid.uuid4(),
#             order_id=uuid.uuid4(),
#             uploaded_by=uuid.uuid4(),
#             s3_object_path="orders/del.jpg",
#         )
#         app.dependency_overrides[get_current_user] = lambda: admin_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getImageImageId=_async(image),
#             delete_order_image=_async(True),
#         )

#         res = http_client.delete(
#             f"/api/v1/order/images/{image.id}", headers=admin_headers
#         )
#         assert res.status_code == 204

#     def test_delete_image_client_always_rejected(
#         self, http_client, client_headers, client_payload
#     ):
#         """Endpoint has is_owner hard-coded to False — clients are always denied."""
#         image = SimpleNamespace(
#             id=uuid.uuid4(),
#             order_id=uuid.uuid4(),
#             uploaded_by=uuid.UUID(client_payload.id),  # even if they uploaded it
#             s3_object_path="orders/x.jpg",
#         )
#         app.dependency_overrides[get_current_user] = lambda: client_payload
#         app.dependency_overrides[get_order_service] = lambda: SimpleNamespace(
#             getImageImageId=_async(image)
#         )

#         res = http_client.delete(
#             f"/api/v1/order/images/{image.id}", headers=client_headers
#         )
#         assert res.status_code == 403
