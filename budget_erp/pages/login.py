import reflex as rx
from ..state.base import BaseState

def login_page() -> rx.Component:
    from ..state.user_state import UserState
    return rx.center(
        rx.cond(
            BaseState.has_users,
            # Normal Login Form
            rx.vstack(
                rx.heading("Login", size="7", margin_bottom="1rem"),
                rx.text("Enter your credentials to access the ERP.", color="gray", margin_bottom="2rem"),
                
                rx.vstack(
                    rx.text("Email", size="2", weight="bold"),
                    rx.input(
                        placeholder="user@example.com", 
                        on_change=BaseState.set_email_field,
                        width="100%",
                    ),
                    width="100%",
                    align_items="start",
                    spacing="2",
                ),
                
                rx.vstack(
                    rx.text("Password", size="2", weight="bold"),
                    rx.input(
                        placeholder="••••••••", 
                        type="password", 
                        on_change=BaseState.set_password_field,
                        width="100%",
                    ),
                    width="100%",
                    align_items="start",
                    spacing="2",
                ),

                rx.cond(
                    BaseState.error_message != "",
                    rx.callout(
                        BaseState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        width="100%",
                    ),
                ),

                rx.button(
                    "Sign In", 
                    on_click=BaseState.login,
                    width="100%",
                    size="3",
                    margin_top="1rem",
                ),
                
                padding="2em",
                width="400px",
                bg=rx.color("gray", 2),
                border=f"1px solid {rx.color('gray', 4)}",
                border_radius="0.5em",
                spacing="4",
            ),
            # Initial Setup Form (First User)
            rx.vstack(
                rx.heading("Initial Setup", size="7", margin_bottom="1rem"),
                rx.text("Create your administrator account to get started.", color="gray", margin_bottom="2rem"),
                
                rx.vstack(
                    rx.text("Full Name", size="2", weight="bold"),
                    rx.input(
                        placeholder="John Doe", 
                        on_change=UserState.set_username,
                        width="100%",
                    ),
                    width="100%",
                    align_items="start",
                    spacing="2",
                ),
                
                rx.vstack(
                    rx.text("Email", size="2", weight="bold"),
                    rx.input(
                        placeholder="admin@example.com", 
                        on_change=UserState.set_email,
                        width="100%",
                    ),
                    width="100%",
                    align_items="start",
                    spacing="2",
                ),
                
                rx.vstack(
                    rx.text("Password", size="2", weight="bold"),
                    rx.input(
                        placeholder="••••••••", 
                        type="password", 
                        on_change=UserState.set_password,
                        width="100%",
                    ),
                    width="100%",
                    align_items="start",
                    spacing="2",
                ),

                rx.button(
                    "Create Administrator", 
                    on_click=UserState.create_first_user,
                    width="100%",
                    size="3",
                    margin_top="1rem",
                    color_scheme="blue",
                ),
                
                padding="2em",
                width="400px",
                bg=rx.color("blue", 2),
                border=f"1px solid {rx.color('blue', 4)}",
                border_radius="0.5em",
                spacing="4",
            ),
        ),
        height="100vh",
        bg=rx.color("gray", 1),
    )
