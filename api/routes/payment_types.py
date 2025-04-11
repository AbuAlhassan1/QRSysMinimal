from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from api.deps import CurrentUser, SessionDep
from models import (
    PaymentType,
    PaymentTypeCreate,
    PaymentTypePublic,
    PaymentTypeUpdate,
    Message,
)

router = APIRouter(prefix="/payment-types", tags=["payment-types"])


@router.get("/", response_model=list[PaymentTypePublic])
def read_payment_types(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve payment types.
    """
    statement = select(PaymentType).offset(skip).limit(limit)
    payment_types = session.exec(statement).all()
    return payment_types


@router.get("/{id}", response_model=PaymentTypePublic)
def read_payment_type(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get payment type by ID.
    """
    payment_type = session.get(PaymentType, id)
    if not payment_type:
        raise HTTPException(status_code=404, detail="Payment type not found")
    return payment_type


@router.post("/", response_model=PaymentTypePublic)
def create_payment_type(
    *, session: SessionDep, current_user: CurrentUser, payment_type_in: PaymentTypeCreate
) -> Any:
    """
    Create new payment type.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    payment_type = PaymentType.model_validate(payment_type_in)
    session.add(payment_type)
    session.commit()
    session.refresh(payment_type)
    return payment_type


@router.put("/{id}", response_model=PaymentTypePublic)
def update_payment_type(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    payment_type_in: PaymentTypeUpdate,
) -> Any:
    """
    Update a payment type.
    """
    payment_type = session.get(PaymentType, id)
    if not payment_type:
        raise HTTPException(status_code=404, detail="Payment type not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = payment_type_in.model_dump(exclude_unset=True)
    payment_type.sqlmodel_update(update_dict)
    session.add(payment_type)
    session.commit()
    session.refresh(payment_type)
    return payment_type


@router.delete("/{id}")
def delete_payment_type(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a payment type.
    """
    payment_type = session.get(PaymentType, id)
    if not payment_type:
        raise HTTPException(status_code=404, detail="Payment type not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(payment_type)
    session.commit()
    return Message(message="Payment type deleted successfully") 