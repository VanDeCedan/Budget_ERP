import reflex as rx
from sqlmodel import Field

class Balance(rx.Model, table=True):
    __tablename__ = "balance"
    
    ptab_id: int = Field(foreign_key="ptab.id", nullable=False, index=True)
    amount: int = Field(nullable=False)
