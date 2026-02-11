import reflex as rx
from sqlmodel import Field

class Travel(rx.Model, table=True):
    __tablename__ = "travel"
    
    sub_request_id: int = Field(foreign_key="sub_request.id", nullable=False)
    travel_type: str = Field(nullable=False) # advance/momo
