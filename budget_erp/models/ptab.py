import reflex as rx
from sqlmodel import Field

class Ptab(rx.Model, table=True):
    __tablename__ = "ptab"
    
    year: int = Field(nullable=False)
    projet: str = Field(nullable=False)
    activities: str = Field(max_length=512, nullable=False)
    projet_code: str = Field(nullable=False)
    result: str = Field(default=None, nullable=True)
    item_code: str = Field(nullable=False)
    activity_code: int = Field(unique=True, nullable=False, index=True)
    amount: int = Field(nullable=False)
    status: str = Field(default="active", index=True, nullable=False) # active/inactive