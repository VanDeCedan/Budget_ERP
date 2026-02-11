import reflex as rx
from sqlmodel import Field

class Request(rx.Model, table=True):
    __tablename__ = "request"
    
    issuer_id: int = Field(foreign_key="issuer.id", nullable=False)
    request_type: str = Field(nullable=False) # travel/purchase
    status: str = Field(default="active", nullable=False) # active/inactive/completed
