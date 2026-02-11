from sqlmodel import SQLModel, create_engine
import reflex as rx
import os

# Import all models to register them with SQLModel metadata
from budget_erp.models.user import User
from budget_erp.models.issuer import Issuer
from budget_erp.models.ptab import Ptab
from budget_erp.models.request import Request
from budget_erp.models.sub_request import SubRequest
from budget_erp.models.expenses import Expenses
from budget_erp.models.travel import Travel
from budget_erp.models.reconciliation import Reconciliation
from budget_erp.models.regularisation import Regularisation
from budget_erp.models.balance import Balance

def init_db():
    db_path = "reflex.db"
    
    # Simple migration: remove old DB to force clean slate with new schema
    # In production, we would use proper migrations (alembic)
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path} to apply new schema...")
        os.remove(db_path)
    
    print("Creating database tables...")
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
