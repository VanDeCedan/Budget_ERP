import reflex as rx
from datetime import datetime
from sqlmodel import Field

class Reconciliation(rx.Model, table=True):
    __tablename__ = "reconciliation"
    
    req_id: int = Field(foreign_key="request.id", nullable=False) # Note: user said <> request.id, essentially FK
    reconci_type: str = Field(nullable=False) # advance/momo/facture
    status: str = Field(default="active", index=True, nullable=False)
    register_by: int = Field(foreign_key="users.id", nullable=False)
    register_at: datetime = Field(default_factory=datetime.utcnow)
