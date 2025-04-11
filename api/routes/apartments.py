from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from api.deps import CurrentUser, SessionDep
from models import (
    ApartmentInfo,
    ApartmentInfoCreate,
    ApartmentInfoPublic,
    ApartmentInfoUpdate,
    Message,
)

router = APIRouter(prefix="/apartments", tags=["apartments"])


@router.get("/", response_model=list[ApartmentInfoPublic])
def read_apartments(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve apartments.
    """
    statement = select(ApartmentInfo).offset(skip).limit(limit)
    apartments = session.exec(statement).all()
    return apartments


@router.get("/{id}", response_model=ApartmentInfoPublic)
def read_apartment(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get apartment by ID.
    """
    apartment = session.get(ApartmentInfo, id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment


@router.post("/", response_model=ApartmentInfoPublic)
def create_apartment(
    *, session: SessionDep, current_user: CurrentUser, apartment_in: ApartmentInfoCreate
) -> Any:
    """
    Create new apartment.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    apartment = ApartmentInfo.model_validate(apartment_in)
    session.add(apartment)
    session.commit()
    session.refresh(apartment)
    return apartment


@router.put("/{id}", response_model=ApartmentInfoPublic)
def update_apartment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    apartment_in: ApartmentInfoUpdate,
) -> Any:
    """
    Update an apartment.
    """
    apartment = session.get(ApartmentInfo, id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = apartment_in.model_dump(exclude_unset=True)
    apartment.sqlmodel_update(update_dict)
    session.add(apartment)
    session.commit()
    session.refresh(apartment)
    return apartment


@router.delete("/{id}")
def delete_apartment(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete an apartment.
    """
    apartment = session.get(ApartmentInfo, id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(apartment)
    session.commit()
    return Message(message="Apartment deleted successfully") 