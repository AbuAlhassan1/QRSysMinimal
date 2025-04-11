import logging
from datetime import date, datetime, timedelta
import random

from sqlmodel import Session, select

from core.db import engine, init_db
from models import (
    ApartmentInfo, 
    ClientInfo, 
    PaymentType, 
    Payment,
    HistoryType,
    History,
    User
)
from crud import create_user
from models import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        # Initialize the database (creates tables and admin user)
        init_db(session)
        
        # Check if we already have seeded data
        apartment_count = session.exec(select(ApartmentInfo)).all()
        if apartment_count:
            logger.info("Data already seeded, skipping...")
            return
            
        logger.info("Seeding database with sample data...")
        
        # Create payment types
        payment_types = [
            PaymentType(name="Cash"),
            PaymentType(name="Credit Card"),
            PaymentType(name="Bank Transfer"),
            PaymentType(name="Check")
        ]
        for pt in payment_types:
            session.add(pt)
        session.commit()
        
        # Create history types
        history_types = [
            HistoryType(name="Login"),
            HistoryType(name="Logout"),
            HistoryType(name="Payment Added"),
            HistoryType(name="Client Added"),
            HistoryType(name="Apartment Added")
        ]
        for ht in history_types:
            session.add(ht)
        session.commit()
        
        # Create apartments
        apartments = []
        for i in range(1, 6):
            apt = ApartmentInfo(
                building=str(random.randint(1, 5)),
                floor=str(random.randint(1, 10)),
                apt_no=str(i * 100 + random.randint(1, 10)),
                area=random.randint(80, 200),
                meter_price=random.randint(1000, 3000),
                apt_type=random.choice(["A1",'A2','A3','A4','B1','B2','B3','B4','B5','B6'])
            )
            session.add(apt)
            apartments.append(apt)
        session.commit()
        
        # Create clients for apartments
        clients = []
        for apt in apartments:
            for j in range(1, 3):  # 2 clients per apartment
                client = ClientInfo(
                    name=f"Client {apt.id}-{j}",
                    id_no=random.randint(1000000, 9999999),
                    issue_date=date.today() - timedelta(days=random.randint(1, 1000)),
                    no=random.randint(1, 1000),
                    m=random.choice(["Cairo", "Alexandria", "Giza"]),
                    z=random.choice(["Zone A", "Zone B", "Zone C"]),
                    d=random.choice(["District 1", "District 2", "District 3"]),
                    phone_number=f"+201{random.randint(10000000, 99999999)}",
                    registry_no=f'{random.randint(1000,10000)}',
                    newspaper_no=f'{random.randint(1,1000)}',
                    job_title=random.choice(["Engineer", "Doctor", "Teacher", "Lawyer", "Accountant"]),
                    alt_name=f"Alternative {apt.id}-{j}",
                    alt_kinship=random.choice(["Spouse", "Parent", "Sibling", "Child"]),
                    alt_phone=f"+201{random.randint(10000000, 99999999)}",
                    alt_m=random.randint(1, 5),
                    alt_z=random.randint(1, 5),
                    alt_d=random.randint(1, 5),
                    created_at=date.today(),
                    apt_id=apt.id
                )
                session.add(client)
                clients.append(client)
        session.commit()
        
        # Create payments for clients
        for client in clients:
            # Create 1-3 payments per client
            for k in range(random.randint(1, 3)):
                payment = Payment(
                    date_of_payment=datetime.now() - timedelta(days=random.randint(1, 365)),
                    payment_type_id=random.choice(payment_types).id,
                    amount=random.randint(1000, 10000),
                    client_id=client.id
                )
                session.add(payment)
        session.commit()
        
        # Create history entries
        for i in range(10):
            history = History(
                type_id=random.choice(history_types).id,
                datetime=datetime.now() - timedelta(days=random.randint(1, 30), 
                                                   hours=random.randint(1, 23), 
                                                   minutes=random.randint(1, 59)),
                                                   entity_id=1
            )
            session.add(history)
        session.commit()
        
        logger.info("Database seeded successfully")


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
