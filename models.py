import uuid
from datetime import date, datetime
from typing import Union, List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: Optional[str] = Field(default=None, max_length=255)  # type: ignore
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    hashed_password: str
    items: List["Item"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete"})


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: str


class UsersPublic(SQLModel):
    data: List[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    owner_id: str = Field(foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: str
    owner_id: str


class ItemsPublic(SQLModel):
    data: List[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: Optional[str] = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Apartment related models
class ApartmentInfoBase(SQLModel):
    building: str
    floor: int
    apt_no: int
    area: int
    meter_price: int
    apt_type: str


class ApartmentInfoCreate(ApartmentInfoBase):
    pass


class ApartmentInfoUpdate(ApartmentInfoBase):
    building: Optional[int] = None
    floor: Optional[int] = None
    apt_no: Optional[int] = None
    area: Optional[int] = None
    meter_price: Optional[int] = None
    apt_type: Optional[str] = None


class ApartmentInfo(ApartmentInfoBase, table=True):
    __tablename__ = "apartment_info"
    id: int = Field(default=None, primary_key=True, index=True)
    clients: List["ClientInfo"] = Relationship(back_populates="apartment")


class ApartmentInfoPublic(ApartmentInfoBase):
    id: int


# Client related models
class ClientInfoBase(SQLModel):
    name: str
    id_no: int
    issue_date: date
    no: int = Field(unique=True)
    m: str
    z: str
    d: str
    phone_number: str
    registry_no : str
    newspaper_no : str
    job_title: str
    alt_name: str
    alt_kinship: str
    alt_phone: str
    alt_m: str
    alt_z: str
    alt_d: str
    created_at: date = Field(default=date.today())
    apt_id: int = Field(foreign_key="apartment_info.id")
    is_formal : int


class ClientInfoCreate(ClientInfoBase):
    pass


class ClientInfoUpdate(ClientInfoBase):
    name: Optional[str] = None
    id_no: Optional[int] = None
    no: Optional[int] = None
    issue_date: Optional[date] = None
    m: Optional[str] = None
    z: Optional[str] = None
    d: Optional[str] = None
    phone_number: Optional[str] = None
    registry_no : Optional[str] = None
    newspaper_no : Optional[str] = None
    job_title: Optional[str] = None
    alt_name: Optional[str] = None
    alt_kinship: Optional[str] = None
    alt_phone: Optional[str] = None
    alt_m: Optional[str] = None
    alt_z: Optional[str] = None
    alt_d: Optional[str] = None
    created_at: Optional[date] = None
    apt_id: Optional[int] = None
    is_formal : Optional[int] = None


class ClientInfo(ClientInfoBase, table=True):
    __tablename__ = "client_info"
    id: int = Field(default=None, primary_key=True, index=True)
    apartment: ApartmentInfo = Relationship(back_populates="clients")
    payments: List["Payment"] = Relationship(back_populates="client")


class ClientInfoPublic(ClientInfoBase):
    id: int


# Payment Type models
class PaymentTypeBase(SQLModel):
    name: str


class PaymentTypeCreate(PaymentTypeBase):
    pass


class PaymentTypeUpdate(PaymentTypeBase):
    name: Optional[str] = None


class PaymentType(PaymentTypeBase, table=True):
    __tablename__ = "payment_type"
    id: int = Field(default=None, primary_key=True, index=True)
    payments: List["Payment"] = Relationship(back_populates="payment_type")


class PaymentTypePublic(PaymentTypeBase):
    id: int


# Payment models
class PaymentBase(SQLModel):
    date_of_payment: datetime
    payment_type_id: int = Field(foreign_key="payment_type.id")
    amount: int
    client_id: int = Field(foreign_key="client_info.id")


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    date_of_payment: Optional[datetime] = None
    payment_type_id: Optional[int] = None
    amount: Optional[int] = None
    client_id: Optional[int] = None


class Payment(PaymentBase, table=True):
    __tablename__ = "payments"
    id: int = Field(default=None, primary_key=True, index=True)
    payment_type: PaymentType = Relationship(back_populates="payments")
    client: ClientInfo = Relationship(back_populates="payments")


class PaymentPublic(PaymentBase):
    id: int


# History Type models
class HistoryTypeBase(SQLModel):
    name: str


class HistoryTypeCreate(HistoryTypeBase):
    pass


class HistoryTypeUpdate(HistoryTypeBase):
    name: Optional[str] = None


class HistoryType(HistoryTypeBase, table=True):
    __tablename__ = "history_types"
    id: int = Field(default=None, primary_key=True, index=True)
    histories: List["History"] = Relationship(back_populates="history_type")


class HistoryTypePublic(HistoryTypeBase):
    id: int


# History models
class HistoryBase(SQLModel):
    type_id: int = Field(foreign_key="history_types.id")
    datetime: datetime
    entity_id : int
    user_id : str


class HistoryCreate(HistoryBase):
    pass


class HistoryUpdate(HistoryBase):
    type_id: Optional[int] = None
    datetime: Optional[datetime] = None
    entity_id : int
    user_id : int


class History(HistoryBase, table=True):
    __tablename__ = "history"
    id: int = Field(default=None, primary_key=True, index=True)
    history_type: HistoryType = Relationship(back_populates="histories")


class HistoryPublic(HistoryBase):
    id: int