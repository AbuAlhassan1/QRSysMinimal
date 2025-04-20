from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from api.deps import CurrentUser, SessionDep
from models import (
    History,
    HistoryCreate,
    HistoryPublic,
    HistoryUpdate,
    HistoryType,
    HistoryTypeCreate,
    HistoryTypePublic,
    HistoryTypeUpdate,
    Message,
    ClientInfo,
    User
)
from pydantic import BaseModel

router = APIRouter(tags=["history"])

# Define a new model for the joined data
class HistoryWithTypePublic(BaseModel):
    id: int
    type_id: int
    datetime: Any
    entity_id: int
    history_type: HistoryTypePublic


# History Types Routes
@router.get("/history-types", response_model=list[HistoryTypePublic], tags=["history-types"])
def read_history_types(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve history types.
    """
    statement = select(HistoryType).offset(skip).limit(limit)
    history_types = session.exec(statement).all()
    return history_types


@router.get("/history-types/{id}", response_model=HistoryTypePublic, tags=["history-types"])
def read_history_type(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get history type by ID.
    """
    history_type = session.get(HistoryType, id)
    if not history_type:
        raise HTTPException(status_code=404, detail="History type not found")
    return history_type


@router.post("/history-types", response_model=HistoryTypePublic, tags=["history-types"])
def create_history_type(
    *, session: SessionDep, current_user: CurrentUser, history_type_in: HistoryTypeCreate
) -> Any:
    """
    Create new history type.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    history_type = HistoryType.model_validate(history_type_in)
    session.add(history_type)
    session.commit()
    session.refresh(history_type)
    return history_type


@router.put("/history-types/{id}", response_model=HistoryTypePublic, tags=["history-types"])
def update_history_type(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    history_type_in: HistoryTypeUpdate,
) -> Any:
    """
    Update a history type.
    """
    history_type = session.get(HistoryType, id)
    if not history_type:
        raise HTTPException(status_code=404, detail="History type not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = history_type_in.model_dump(exclude_unset=True)
    history_type.sqlmodel_update(update_dict)
    session.add(history_type)
    session.commit()
    session.refresh(history_type)
    return history_type


@router.delete("/history-types/{id}", tags=["history-types"])
def delete_history_type(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a history type.
    """
    history_type = session.get(HistoryType, id)
    if not history_type:
        raise HTTPException(status_code=404, detail="History type not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(history_type)
    session.commit()
    return Message(message="History type deleted successfully")


# # History Entries Routes
# @router.get("/history", response_model=list[HistoryPublic], tags=["history-entries"])
# def read_histories(
#     session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
# ) -> Any:
#     """
#     Retrieve history entries.
#     """
#     statement = select(History).offset(skip).limit(limit)
#     histories = session.exec(statement).all()
#     return histories


@router.get("/history", response_model=list[dict], tags=["history-entries"])
def read_histories_with_types(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve history entries with joined history type data.
    """
    # Using relationship loading
    statement = select(History).offset(skip).limit(limit)
    histories = session.exec(statement).all()
    
    # Manually construct the response with nested history_type data
    result = []
    for history in histories:
        history_type = session.get(HistoryType, history.type_id)
        history_data = {
            "id": history.id,
            "type_id": history.type_id,
            "datetime": history.datetime,
            "entity_id": history.entity_id,
            "history_type": {
                "id": history_type.id,
                "name": history_type.name
            },
            "user_info" :{
                "name" : current_user.full_name
            }
        }
        result.append(history_data)
    
    return result


@router.get("/history/by-type/{type_id}", response_model=list[HistoryPublic], tags=["history-entries"])
def read_histories_by_type(
    session: SessionDep, current_user: CurrentUser, type_id: int
) -> Any:
    """
    Get history entries by type ID.
    """
    statement = select(History).where(History.type_id == type_id)
    histories = session.exec(statement).all()
    return histories


@router.get("/history/{id}", response_model=HistoryPublic, tags=["history-entries"])
def read_history(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get history entry by ID.
    """
    history = session.get(History, id)
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    return history


@router.post("/history", response_model=HistoryPublic, tags=["history-entries"])
def create_history(
    *, session: SessionDep, current_user: CurrentUser, history_in: HistoryCreate
) -> Any:
    """
    Create new history entry.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    history = History.model_validate(history_in)
    session.add(history)
    session.commit()
    session.refresh(history)
    return history


@router.put("/history/{id}", response_model=HistoryPublic, tags=["history-entries"])
def update_history(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    history_in: HistoryUpdate,
) -> Any:
    """
    Update a history entry.
    """
    history = session.get(History, id)
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_dict = history_in.model_dump(exclude_unset=True)
    history.sqlmodel_update(update_dict)
    session.add(history)
    session.commit()
    session.refresh(history)
    return history


@router.delete("/history/{id}", tags=["history-entries"])
def delete_history(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a history entry.
    """
    history = session.get(History, id)
    if not history:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(history)
    session.commit()
    return Message(message="History entry deleted successfully")