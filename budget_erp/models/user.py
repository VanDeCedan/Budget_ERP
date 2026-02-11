import reflex as rx
from sqlmodel import Field
from datetime import datetime

class User(rx.Model, table=True):
    __tablename__ = "users" # Explicit table name as requested
    
    mail: str = Field(unique=True, index=True, nullable=False) # Hashed
    password: str = Field(nullable=False) # Hashed
    name: str = Field(nullable=False) # Encrypted
    role: str = Field(nullable=False) # admin/budget
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(nullable=False)
    status: str = Field(default="active", index=True, nullable=False) # active/inactive
