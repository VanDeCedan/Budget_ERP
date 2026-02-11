import reflex as rx
from datetime import datetime
from sqlmodel import Field

class Budget(rx.Model, table=True):
    name: str
    amount: float
    period: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
