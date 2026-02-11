import reflex as rx
from sqlmodel import Field
from datetime import datetime

class SubRequest(rx.Model, table=True):
    __tablename__ = "sub_request"
    
    req_id: int = Field(foreign_key="request.id", nullable=False)
    sub_request_type: str = Field(nullable=False, index=True) # initial/add
    object: str = Field(nullable=True, max_length=255)
    status: str = Field(default="active", index=True, nullable=False)
    register_by: int = Field(foreign_key="users.id", nullable=False)
    register_at: datetime = Field(default_factory=datetime.utcnow)
