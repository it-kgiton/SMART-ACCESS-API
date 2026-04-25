from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse, ClientSetPin
from app.services.client_service import ClientService
from app.dependencies import get_current_user, require_any_role

router = APIRouter()


@router.post("/")
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "parent")),
):
    service = ClientService(db)
    client = await service.create(data)
    return {"success": True, "data": ClientResponse.model_validate(client)}


@router.get("")
async def list_clients(
    school_id: Optional[str] = None, parent_id: Optional[str] = None,
    search: Optional[str] = None, status: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "parent", "merchant")),
):
    service = ClientService(db)
    clients, total = await service.list(
        school_id=school_id, parent_id=parent_id, search=search,
        status=status, skip=skip, limit=limit,
    )
    return {
        "success": True,
        "data": [ClientResponse.model_validate(c) for c in clients],
        "total": total,
    }


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ClientService(db)
    client = await service.get_by_id(client_id)
    if not client:
        raise NotFoundException("Client")
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str, data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "parent")),
):
    service = ClientService(db)
    return await service.update(client_id, data)


@router.post("/{client_id}/set-pin")
async def set_client_pin(
    client_id: str, data: ClientSetPin,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "parent")),
):
    service = ClientService(db)
    await service.set_pin(client_id, data.pin)
    return {"success": True, "message": "PIN updated"}


@router.post("/{client_id}/suspend")
async def suspend_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = ClientService(db)
    client = await service.suspend(client_id)
    return {"success": True, "data": ClientResponse.model_validate(client)}


@router.post("/{client_id}/activate")
async def activate_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = ClientService(db)
    client = await service.activate(client_id)
    return {"success": True, "data": ClientResponse.model_validate(client)}


@router.post("/{client_id}/lock")
async def lock_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = ClientService(db)
    client = await service.lock(client_id)
    return {"success": True, "data": ClientResponse.model_validate(client)}


@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = ClientService(db)
    await service.delete(client_id)
    return {"success": True, "message": "Client deleted"}
