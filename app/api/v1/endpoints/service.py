from app.core.dependencies import ServiceServiceDep
from app.core.security import JWTBearer, decode_access_token, RoleChecker
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


allow_admin = RoleChecker(["admin"])
router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=ServiceResponse,dependencies=[Depends(JWTBearer()),Depends(allow_admin)])
async def add_service(service: ServiceCreate, serviceDep:ServiceServiceDep):
    return await serviceDep.add(service)

@router.get("/", response_model=List[ServiceResponse],dependencies=[Depends(JWTBearer())])
async def list_services(service: ServiceServiceDep ):
    return await service.get()

@router.get("/{id}", response_model=ServiceResponse,dependencies=[Depends(JWTBearer())])
async def get_service(id, service: ServiceServiceDep):
    return await service.getId(id)

@router.delete("/{id}",dependencies=[Depends(JWTBearer())])
async def delete_service(id, service: ServiceServiceDep):
    return await service.remove(id)


@router.put("/{id}", response_model=ServiceResponse,dependencies=[Depends(JWTBearer())])
async def update_service(id,updateService:ServiceUpdate,service:ServiceServiceDep,skip: int = 0, limit: int = 10):
    return await service.update(id,updateService)


