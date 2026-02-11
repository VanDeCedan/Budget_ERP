import reflex as rx
from sqlmodel import Field

class Regularisation(rx.Model, table=True):
    __tablename__ = "regularisation"
    
    expenses_id: int = Field(foreign_key="expenses.id", nullable=False)
    reconci_id: int = Field(foreign_key="reconciliation.id", nullable=False)
    amount: int = Field(nullable=False)
