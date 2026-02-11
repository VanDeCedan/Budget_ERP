import reflex as rx
from ..state.base import BaseState
from ..state.auth_state import AuthState

def sidebar_item(text: str, icon: str, url: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, font_weight="medium"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "border-radius": "0.5em",
            },
        ),
        href=url,
        underline="none",
        width="100%",
    )

def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Budget ERP", font_size="1.5em", font_weight="bold", color=rx.color("accent", 11)),
            rx.divider(),
            sidebar_item("Dashboard", "layout-dashboard", "/"),
            rx.cond(
                AuthState.is_admin,
                sidebar_item("Users", "users", "/users"),
            ),
            sidebar_item("Demandeurs", "building-2", "/issuers"),
            sidebar_item("Budgets", "wallet", "/budgets"),
            sidebar_item("Requêtes", "banknote", "/requests"),
            sidebar_item("Reconciliations", "arrow-left-right", "/reconciliations"),
            sidebar_item("Solde", "pie-chart", "/solde"),
            spacing="4",
            padding="1em",
            height="100%",
        ),
        height="100vh",
        width="250px",
        position="sticky",
        top="0",
        border_right=f"1px solid {rx.color('gray', 4)}",
        background_color=rx.color("gray", 2),
    )
