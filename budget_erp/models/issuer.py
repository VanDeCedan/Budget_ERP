import reflex as rx
from sqlmodel import Field
from datetime import datetime

class Issuer(rx.Model, table=True):
    __tablename__ = "issuer"
    
    name: str = Field(nullable=False) # Encrypted
    name_index: str = Field(nullable=False, index=True) # Hashed
    department: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(nullable=False)
    status: str = Field(default="active", index=True, nullable=False) # active/inactive
