import os
import reflex as rx

config = rx.Config(
    app_name="budget_erp",
    db_url="sqlite:///reflex.db",
    api_url=os.getenv("API_URL", "http://localhost:8000"),
)
