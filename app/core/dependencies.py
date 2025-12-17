from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# from app.core.security import decode_access_token, oauth2_scheme
# from app.database.models import Seller

from app.db.session import get_session
# from app.services.seller import SellerService
# from app.services.shipment import ShipmentService
from app.services.service import ServiceService
from app.services.user_service import UserService



# Asynchronous database session dep annotation
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# # Access token data dep
# def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
#     data = decode_access_token(token)

#     if data is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired access token",
#         )

#     return data


# # Logged In Seller
# async def get_current_seller(
#     token_data: Annotated[dict, Depends(get_access_token)],
#     session: SessionDep,
# ):
#     return await session.get(Seller, token_data["user"]["id"])


# Shipment service dep
def get_user_service(session: SessionDep):
    return UserService(session)

def get_service(session:SessionDep):
    return ServiceService(session)



# Shipment service dep annotation
UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]

ServiceServiceDep = Annotated[ServiceService,Depends(get_service),]
