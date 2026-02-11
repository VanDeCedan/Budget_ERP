import reflex as rx
from .sidebar import sidebar
from .navbar import navbar

def layout(content: rx.Component) -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            navbar(),
            rx.box(
                content,
                padding="2em",
                width="100%",
            ),
            width="100%",
            display="flex",
            flex_direction="column",
        ),
        width="100%",
        spacing="0",
    )
