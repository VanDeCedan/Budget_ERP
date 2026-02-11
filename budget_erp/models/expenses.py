import reflex as rx
from sqlmodel import Field

class Expenses(rx.Model, table=True):
    __tablename__ = "expenses"
    
    ptab_id: int = Field(foreign_key="ptab.id", nullable=False)
    sub_request_id: int = Field(foreign_key="sub_request.id", nullable=False)
    amount: int = Field(nullable=False)
