from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select, SQLModel

from api.deps import CurrentUser, SessionDep
from models import (
    ApartmentInfo,
    ApartmentInfoCreate,
    ClientInfo,
    ClientInfoCreate,
    Payment,
    PaymentCreate,
    Message,
)

router = APIRouter(prefix="/combined-operations", tags=["combined-operations"])


class ApartmentClientPaymentCreate(SQLModel):
    """Schema for creating apartment, client, and payment in one request"""
    apartment: ApartmentInfoCreate
    client: ClientInfoCreate
    payment: PaymentCreate


class ApartmentClientPaymentResponse(SQLModel):
    """Response schema for the combined creation"""
    apartment_id: int
    client_id: int
    payment_id: int


@router.post("/apartment-client-payment", response_model=ApartmentClientPaymentResponse)
def create_apartment_client_payment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: ApartmentClientPaymentCreate
) -> Any:
    """
    Create a new apartment, client, and payment in a single transaction.
    """
    # Check permissions
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Create apartment
    apartment = ApartmentInfo.model_validate(data.apartment)
    session.add(apartment)
    session.flush()  # Flush to get the apartment ID without committing
    
    # Create client with the apartment ID
    client_data = data.client.model_dump()
    client_data["apt_id"] = apartment.id  # Set the apartment ID
    client = ClientInfo.model_validate(client_data)
    if 'c' in apartment.building or 'C' in apartment.building:
        client.is_formal = 0
    session.add(client)
    session.flush()  # Flush to get the client ID without committing
    
    # Create payment with the client ID
    payment_data = data.payment.model_dump()
    payment_data["client_id"] = client.id  # Set the client ID
    payment = Payment.model_validate(payment_data)
    session.add(payment)
    
    # Commit the transaction
    try:
        session.commit()
        session.refresh(apartment)
        session.refresh(client)
        session.refresh(payment)
        
        return ApartmentClientPaymentResponse(
            apartment_id=apartment.id,
            client_id=client.id,
            payment_id=payment.id
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating records: {str(e)}")


@router.delete("/apartment-client-payment/{client_id}", response_model=ApartmentClientPaymentResponse)
def delete_apartment_client_payment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    client_id: int
) -> Any:
    """
    Delete apartment, client, and payment in a single transaction based on client ID.
    """
    # Check permissions
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        # Find the client first
        client = session.exec(
            select(ClientInfo).where(ClientInfo.id == client_id)
        ).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Find and delete all associated payments
        payments = session.exec(
            select(Payment).where(Payment.client_id == client_id)
        ).all()
        payment_id = 0
        for payment in payments:
            payment_id = payment.id  # Store the last payment ID for response
            session.delete(payment)
        session.flush()
        
        # Get apartment ID before deleting client
        apartment_id = client.apt_id
        
        # Delete the client
        session.delete(client)
        session.flush()
        
        # Find and delete apartment if no other clients are using it
        remaining_clients = session.exec(
            select(ClientInfo).where(ClientInfo.apt_id == apartment_id)
        ).all()
        
        if not remaining_clients:  # Only delete apartment if no other clients are using it
            apartment = session.get(ApartmentInfo, apartment_id)
            if apartment:
                session.delete(apartment)
        
        # Commit the transaction
        session.commit()
        
        return ApartmentClientPaymentResponse(
            apartment_id=apartment_id,
            client_id=client_id,
            payment_id=payment_id
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting records: {str(e)}")