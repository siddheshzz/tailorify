from typing import List

from fastapi import APIRouter, Depends

from app.core.dependencies import ServiceServiceDep
from app.core.security import RoleChecker
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate

allow_admin = RoleChecker(["admin"])
router = APIRouter()


@router.post(
    "/",
    response_model=ServiceResponse,
    dependencies=[Depends(allow_admin)],
)
async def add_service(service: ServiceCreate, serviceDep: ServiceServiceDep):
    return await serviceDep.add(service)


@router.get("/", response_model=List[ServiceResponse])
async def list_services(service: ServiceServiceDep):
    return await service.get()


@router.get("/{id}", response_model=ServiceResponse)
async def get_service(id, service: ServiceServiceDep):
    return await service.getId(id)


@router.delete("/{id}", dependencies=[Depends(allow_admin)])
async def delete_service(id, service: ServiceServiceDep):
    return await service.remove(id)


@router.put(
    "/{id}", response_model=ServiceResponse, dependencies=[Depends(allow_admin)]
)
async def update_service(
    id,
    updateService: ServiceUpdate,
    service: ServiceServiceDep,
    skip: int = 0,
    limit: int = 10,
):
    return await service.update(id, updateService)
