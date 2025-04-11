from sqladmin import Admin, ModelView
from models import (
    User, 
    Item, 
    ApartmentInfo, 
    ClientInfo, 
    PaymentType, 
    Payment, 
    HistoryType, 
    History
)
from core.db import engine
from fastapi import FastAPI, Depends, Request, HTTPException
from core.security import get_password_hash
from sqlmodel import Session
from wtforms import Form, StringField, BooleanField, PasswordField
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend
from crud import authenticate
import jwt
from core.security import ALGORITHM
from core.config import settings

# Function to get a database session
def get_session():
    with Session(engine) as session:
        yield session

# Custom authentication backend for the admin panel
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        
        # Validate credentials using existing authentication method
        with Session(engine) as session:
            user = authenticate(session=session, email=email, password=password)
            
            if not user:
                return False
            
            # Check if user is active and has admin privileges
            if not user.is_active or not user.is_superuser:
                return False
            
            # Set the user ID in the session
            request.session["user_id"] = str(user.id)
            return True
    
    async def logout(self, request: Request) -> bool:
        # Clear session data
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        # Check if user is authenticated through session
        user_id = request.session.get("user_id")
        if not user_id:
            return False
        
        # Validate that the user still exists in the database
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user or not user.is_active or not user.is_superuser:
                return False
            
        return True

def setup_admin(app: FastAPI) -> None:
    """
    Configure and setup SQLAdmin dashboard
    """
    # Create authentication backend
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    
    # Initialize admin with authentication
    admin = Admin(
        app, 
        engine,
        authentication_backend=authentication_backend,
        title="QR System Admin"
    )

    class UserAdmin(ModelView, model=User):
        column_list = ["id", "email", "is_active", "is_superuser", "full_name"]
        column_searchable_list = ["email", "full_name"]
        column_sortable_list = ["email", "is_active", "is_superuser"]
        column_default_sort = [("email", False)]
        
        # Don't show hashed_password in the form
        form_excluded_columns = ["hashed_password"]
        
        # Permissions
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        icon = "fa-solid fa-user"
        name = "User"
        name_plural = "Users"
        
        # Create a custom form with password field
        async def scaffold_form(self, rules=None):
            form = await super().scaffold_form(rules)
            form.password = PasswordField("Password")
            return form
        
        # This hook runs just before saving the model
        async def on_model_change(self, data, model, is_created, request=None):
            # Get password from submitted data
            password_field = "password"
            if password_field in data:
                # Extract the password value
                password = data.pop(password_field)
                if password:
                    # Hash the password and store it in the hashed_password field
                    model.hashed_password = get_password_hash(password)
            # New users must have a password
            elif is_created and not getattr(model, "hashed_password", None):
                raise ValueError("Password is required for new users")

    class ItemAdmin(ModelView, model=Item):
        column_list = ["id", "title", "description", "owner_id"]
        column_searchable_list = ["title", "description"]
        column_sortable_list = ["title"]
        column_default_sort = [("title", False)]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        icon = "fa-solid fa-box"
        name = "Item"
        name_plural = "Items"
        
    # New admin views for our models
    class ApartmentInfoAdmin(ModelView, model=ApartmentInfo):
        column_list = ["id", "building", "floor", "apt_no", "user_id", "area", "meter_price", "full_price"]
        column_searchable_list = ["building", "floor", "apt_no"]
        column_sortable_list = ["building", "floor", "apt_no", "area", "full_price"]
        column_default_sort = [("building", True), ("floor", True), ("apt_no", True)]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        icon = "fa-solid fa-building"
        name = "Apartment"
        name_plural = "Apartments"
        
    class ClientInfoAdmin(ModelView, model=ClientInfo):
        column_list = ["id", "name", "id_no", "phone_number", "job_title", "apt_id"]
        column_searchable_list = ["name", "id_no", "phone_number"]
        column_sortable_list = ["name", "id_no"]
        column_default_sort = [("name", False)]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        icon = "fa-solid fa-user-group"
        name = "Client"
        name_plural = "Clients"
        
    class PaymentTypeAdmin(ModelView, model=PaymentType):
        column_list = ["id", "name"]
        column_searchable_list = ["name"]
        column_sortable_list = ["name"]
        column_default_sort = [("name", False)]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        icon = "fa-solid fa-credit-card"
        name = "Payment Type"
        name_plural = "Payment Types"
        
    class PaymentAdmin(ModelView, model=Payment):
        column_list = ["id", "date_of_payment", "payment_type_id", "amount", "client_id"]
        column_searchable_list = ["client_id", "payment_type_id"]
        column_sortable_list = ["date_of_payment", "amount"]
        column_default_sort = [("date_of_payment", True)]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        icon = "fa-solid fa-money-bill"
        name = "Payment"
        name_plural = "Payments"
        
    class HistoryTypeAdmin(ModelView, model=HistoryType):
        column_list = ["id", "name"]
        column_searchable_list = ["name"]
        column_sortable_list = ["name"]
        column_default_sort = [("name", False)]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        icon = "fa-solid fa-list-check"
        name = "History Type"
        name_plural = "History Types"
        
    class HistoryAdmin(ModelView, model=History):
        column_list = ["id", "type_id", "datetime"]
        column_searchable_list = ["type_id"]
        column_sortable_list = ["datetime"]
        column_default_sort = [("datetime", True)]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        icon = "fa-solid fa-history"
        name = "History Entry"
        name_plural = "History Entries"

    admin.add_view(UserAdmin)
    admin.add_view(ItemAdmin)
    admin.add_view(ApartmentInfoAdmin)
    admin.add_view(ClientInfoAdmin)
    admin.add_view(PaymentTypeAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(HistoryTypeAdmin)
    admin.add_view(HistoryAdmin)
    
    return admin 