from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from api.deps import CurrentUser, SessionDep
from models import (
    Payment,
    PaymentCreate,
    PaymentPublic,
    PaymentUpdate,
    Message,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_model=list[PaymentPublic])
def read_payments(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve payments.
    """
    statement = select(Payment).offset(skip).limit(limit)
    payments = session.exec(statement).all()
    return payments


@router.get("/by-client/{client_id}", response_model=list[PaymentPublic])
def read_payments_by_client(
    session: SessionDep, current_user: CurrentUser, client_id: int
) -> Any:
    """
    Get payments by client ID.
    """
    statement = select(Payment).where(Payment.client_id == client_id)
    payments = session.exec(statement).all()
    return payments


@router.get("/{id}", response_model=PaymentPublic)
def read_payment(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get payment by ID.
    """
    payment = session.get(Payment, id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/", response_model=PaymentPublic)
def create_payment(
    *, session: SessionDep, current_user: CurrentUser, payment_in: PaymentCreate
) -> Any:
    """
    Create new payment.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    payment = Payment.model_validate(payment_in)
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@router.put("/{id}", response_model=PaymentPublic)
def update_payment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    payment_in: PaymentUpdate,
) -> Any:
    """
    Update a payment.
    """
    payment = session.get(Payment, id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = payment_in.model_dump(exclude_unset=True)
    payment.sqlmodel_update(update_dict)
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@router.delete("/{id}")
def delete_payment(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a payment.
    """
    payment = session.get(Payment, id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(payment)
    session.commit()
    return Message(message="Payment deleted successfully") 