import reflex as rx
from ..state.base import BaseState

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text("Dashboard", font_size="1.2em", font_weight="bold"), 
            rx.spacer(),
            rx.menu.root(
                rx.menu.trigger(
                    rx.hstack(
                        rx.avatar(fallback=BaseState.clear_initials, size="2", cursor="pointer"),
                        rx.text(BaseState.clear_name, size="2", weight="medium", cursor="pointer"),
                        align="center",
                        spacing="2",
                    ),
                ),
                rx.menu.content(
                    rx.menu.item(
                        rx.hstack(
                            rx.icon("user", size=16),
                            rx.text(BaseState.clear_name, size="2"),
                        ),
                        disabled=True,
                    ),
                    rx.menu.item(
                        rx.hstack(
                            rx.icon("shield", size=16),
                            rx.text(BaseState.current_user.role, size="2"),
                        ),
                        disabled=True,
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        rx.hstack(
                            rx.icon("log-out", size=16),
                            rx.text("Déconnexion"),
                        ),
                        on_click=BaseState.logout,
                        color_scheme="red",
                    ),
                ),
            ),
            width="100%",
            padding="1em",
            align="center",
            border_bottom=f"1px solid {rx.color('gray', 4)}",
            background_color=rx.color("gray", 2),
        ),
        position="sticky",
        top="0",
        z_index="100",
    )
