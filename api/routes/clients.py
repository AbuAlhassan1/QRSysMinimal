from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select, or_, and_

from api.deps import CurrentUser, SessionDep
from models import (
    ClientInfo,
    ClientInfoCreate,
    ClientInfoPublic,
    ClientInfoUpdate,
    Message,
    ApartmentInfo,
)

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=list[ClientInfoPublic])
def read_clients(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve clients.
    """
    statement = select(ClientInfo).offset(skip).limit(limit)
    clients = session.exec(statement).all()
    return clients


@router.get("/filter", response_model=list[ClientInfoPublic])
def filter_clients(
    session: SessionDep,
    current_user: CurrentUser,
    name: Optional[str] = None,
    id_no: Optional[int] = None,
    phone_number: Optional[str] = None,
    building: Optional[int] = None,
    floor: Optional[int] = None,
    apt_no: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Filter clients by name, ID number, phone number, and apartment information.
    """
    # Start with a base query joining ClientInfo with ApartmentInfo
    query = select(ClientInfo).join(ApartmentInfo, ClientInfo.apt_id == ApartmentInfo.id)
    
    # Apply filters based on provided parameters
    filters = []
    
    if name:
        filters.append(ClientInfo.name.contains(name))
    
    if id_no:
        filters.append(ClientInfo.id_no.contains(str(id_no)))
    
    if phone_number:
        filters.append(ClientInfo.phone_number.contains(phone_number))
    
    # Apartment filters
    if building:
        filters.append(ApartmentInfo.building.contains(str(building)))
    
    if floor:
        filters.append(ApartmentInfo.floor.contains(str(floor)))
    
    if apt_no:
        filters.append(ApartmentInfo.apt_no.contains(str(apt_no)))
    
    # Apply all filters if any exist
    if filters:
        query = query.where(and_(*filters))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query and return results
    clients = session.exec(query).all()
    return clients


@router.get("/by-apartment/{apt_id}", response_model=list[ClientInfoPublic])
def read_clients_by_apartment(
    session: SessionDep, current_user: CurrentUser, apt_id: int
) -> Any:
    """
    Get clients by apartment ID.
    """
    statement = select(ClientInfo).where(ClientInfo.apt_id == apt_id)
    clients = session.exec(statement).all()
    return clients


@router.get("/{id}", response_model=ClientInfoPublic)
def read_client(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get client by ID.
    """
    client = session.get(ClientInfo, id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("/", response_model=ClientInfoPublic)
def create_client(
    *, session: SessionDep, current_user: CurrentUser, client_in: ClientInfoCreate
) -> Any:
    """
    Create new client.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    client = ClientInfo.model_validate(client_in)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.put("/{id}", response_model=ClientInfoPublic)
def update_client(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    client_in: ClientInfoUpdate,
) -> Any:
    """
    Update a client.
    """
    client = session.get(ClientInfo, id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = client_in.model_dump(exclude_unset=True)
    client.sqlmodel_update(update_dict)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@router.delete("/{id}")
def delete_client(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a client.
    """
    client = session.get(ClientInfo, id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(client)
    session.commit()
    return Message(message="Client deleted successfully")