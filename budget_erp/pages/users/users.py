import reflex as rx
from ...state.user_state import UserState
from ...components.layout import layout
from ...models.user import User

def user_row(user_dict: dict) -> rx.Component:
    user = user_dict["user_obj"]
    return rx.table.row(
        rx.table.cell(user_dict["name"]), 
        rx.table.cell(user_dict["role"]),
        rx.table.cell(
            rx.badge(
                user_dict["status"],
                color_scheme=rx.cond(user_dict["status"] == "active", "green", "red"),
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.button("Edit", on_click=lambda: UserState.open_edit_dialog(user), variant="soft"),
                rx.cond(
                    user_dict["status"] == "active",
                    rx.button(
                        "Deactivate", 
                        on_click=lambda: UserState.open_confirm_dialog(user, "deactivate"),
                        color_scheme="red",
                        variant="surface",
                    ),
                    rx.button(
                        "Activate", 
                        on_click=lambda: UserState.open_confirm_dialog(user, "activate"),
                        color_scheme="green",
                        variant="surface",
                    ),
                ),
            )
        ),
    )

def add_user_form() -> rx.Component:
    return rx.vstack(
        rx.text("Enregistrer un utilisateur", font_size="1.5em", font_weight="bold"),
        rx.input(placeholder="Nom et prénoms", value=UserState.username, on_change=UserState.set_username),
        rx.input(placeholder="Mail", value=UserState.email, on_change=UserState.set_email),
        rx.input(placeholder="Mot de passe", type="password", value=UserState.password, on_change=UserState.set_password),
        rx.select(
            ["admin", "budget"],
            placeholder="Role",
            value=UserState.role,
            on_change=UserState.set_role
        ),
        rx.hstack(
            rx.button("Annuler", on_click=UserState.close_add_dialog, variant="soft", color_scheme="gray"),
            rx.button("Enregistrer", on_click=UserState.add_user),
        ),
        spacing="4",
    )

def edit_user_form() -> rx.Component:
    return rx.vstack(
        rx.text("Modifier un utilisateur", font_size="1.5em", font_weight="bold"),
        rx.text(f"User: {UserState.username}"), # Display selected user name
        rx.select(
            ["admin", "budget"],
            placeholder="Role",
            value=UserState.role,
            on_change=UserState.set_role
        ),
        rx.hstack(
            rx.button("Annuler", on_click=UserState.close_edit_dialog, variant="soft", color_scheme="gray"),
            rx.button("Modifier", on_click=UserState.update_user),
        ),
        spacing="4",
    )

def users_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.text("Gestion des utilisateurs", font_size="2em", font_weight="bold"),
                rx.spacer(),
                rx.button("Enregistrer un utilisateur", on_click=UserState.open_add_dialog),
                width="100%",
                align="center",
            ),
            rx.text("Liste des utilisateurs", font_size="0.8em", color="gray"),
            # Filter Bar
            rx.flex(
                rx.input(
                    placeholder="Filtrer par nom...",
                    value=UserState.search_name,
                    on_change=UserState.set_search_name,
                    size="1",
                    width="250px"
                ),
                rx.select(
                    ["active", "inactive"],
                    value=UserState.search_status,
                    on_change=UserState.set_search_status,
                    size="1",
                    width="120px"
                ),
                rx.button(
                    "Filtrer",
                    on_click=UserState.apply_filters,
                    size="1",
                    color_scheme="blue"
                ),
                rx.button(
                    "Reset",
                    on_click=UserState.reset_filters,
                    size="1",
                    variant="soft",
                    color_scheme="gray"
                ),
                spacing="3",
                align="center",
                wrap="wrap",
                width="100%",
                padding_y="2"
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Nom"),
                        rx.table.column_header_cell("Role"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Actions"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(UserState.display_users, user_row)
                ),
                width="100%",
            ),
            
            # Dialogs
            rx.dialog.root(
                rx.dialog.content(add_user_form()),
                open=UserState.is_add_open,
                on_open_change=UserState.set_is_add_open,
            ),
            rx.dialog.root(
                rx.dialog.content(edit_user_form()),
                open=UserState.is_edit_open,
                on_open_change=UserState.set_is_edit_open,
            ),
            
            # Confirmation Dialog
            rx.dialog.root(
                rx.dialog.content(
                    rx.vstack(
                        rx.heading("Confirmation", size="5"),
                        rx.text(UserState.confirm_message),
                        rx.hstack(
                            rx.button("Annuler", on_click=UserState.close_confirm_dialog, variant="soft", color_scheme="gray"),
                            rx.button("Confirmer", on_click=UserState.handle_confirm_action, color_scheme="red"),
                            width="100%",
                            justify="end",
                            spacing="3",
                        ),
                        spacing="4",
                        padding="1em",
                    )
                ),
                open=UserState.is_confirm_open,
                on_open_change=UserState.set_is_confirm_open,
            ),
            
            width="100%",
            spacing="4",
            on_mount=UserState.load_users,
        )
    )
