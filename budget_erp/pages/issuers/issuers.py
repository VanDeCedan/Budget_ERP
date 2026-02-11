import reflex as rx
from ...state.issuer_state import IssuerState
from ...components.layout import layout
from ...models.issuer import Issuer

def issuer_row(issuer: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(issuer["name"]),
        rx.table.cell(issuer["department"]),
        rx.table.cell(
            rx.badge(
                issuer["status"],
                color_scheme=rx.cond(issuer["status"] == "active", "green", "red"),
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.button("Modifier", on_click=lambda: IssuerState.open_edit_dialog(issuer), variant="soft"),
                rx.cond(
                    issuer["status"] == "active",
                    rx.button(
                        "Désactiver", 
                        on_click=lambda: IssuerState.delete_issuer(issuer),
                        color_scheme="red",
                        variant="surface",
                    ),
                    rx.button(
                        "Activer", 
                        on_click=lambda: IssuerState.activate_issuer(issuer),
                        color_scheme="green",
                        variant="surface",
                    ),
                ),
            )
        ),
    )

def add_issuer_form() -> rx.Component:
    return rx.vstack(
        rx.text("Enregistrer un demandeur", font_size="1.5em", font_weight="bold"),
        rx.input(placeholder="Nom et prénoms", value=IssuerState.name, on_change=IssuerState.set_name),
        rx.select(
            ["ARS3", "DRSE", "DRHA", "DDSR", "DMCC", "DFA"],
            placeholder="Département",
            value=IssuerState.department,
            on_change=IssuerState.set_department
        ),
        rx.hstack(
            rx.button("Annuler", on_click=IssuerState.close_add_dialog, variant="soft", color_scheme="gray"),
            rx.button("Enregistrer", on_click=IssuerState.add_issuer),
        ),
        spacing="4",
    )

def edit_issuer_form() -> rx.Component:
    return rx.vstack(
        rx.text("Modifier un demandeur", font_size="1.5em", font_weight="bold"),
        rx.text(f"Demandeur: {IssuerState.name}"),
        rx.select(
            ["ARS3", "DRSE", "DRHA", "DDSR", "DMCC", "DFA"],
            placeholder="Département",
            value=IssuerState.department,
            on_change=IssuerState.set_department
        ),
        rx.hstack(
            rx.button("Annuler", on_click=IssuerState.close_edit_dialog, variant="soft", color_scheme="gray"),
            rx.button("Modifier", on_click=IssuerState.update_issuer),
        ),
        spacing="4",
    )

def issuers_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.text("Gestion des demandeurs", font_size="2em", font_weight="bold"),
                rx.spacer(),
                rx.button("Enregistrer un demandeur", on_click=IssuerState.open_add_dialog),
                width="100%",
                align="center",
            ),
            rx.text("Liste des demandeurs", font_size="0.8em", color="gray"),
            # Filter Bar
            rx.flex(
                rx.input(
                    placeholder="Filtrer par nom...",
                    value=IssuerState.search_name,
                    on_change=IssuerState.set_search_name,
                    size="1",
                    width="200px"
                ),
                rx.select(
                    ["all", "ARS3", "DRSE", "DRHA", "DDSR", "DMCC", "DFA"],
                    value=IssuerState.search_dept,
                    on_change=IssuerState.set_search_dept,
                    size="1",
                    width="120px"
                ),
                rx.select(
                    ["all", "active", "inactive"],
                    value=IssuerState.search_status,
                    on_change=IssuerState.set_search_status,
                    size="1",
                    width="120px"
                ),
                rx.button(
                    "Filtrer",
                    on_click=IssuerState.apply_filters,
                    size="1",
                    color_scheme="blue"
                ),
                rx.button(
                    "Reset",
                    on_click=IssuerState.reset_filters,
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
                        rx.table.column_header_cell("Département"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Actions"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(IssuerState.display_issuers, issuer_row)
                ),
                width="100%",
            ),
             # Dialogs
            rx.dialog.root(
                rx.dialog.content(add_issuer_form()),
                open=IssuerState.is_add_open,
                on_open_change=IssuerState.set_is_add_open,
            ),
            rx.dialog.root(
                rx.dialog.content(edit_issuer_form()),
                open=IssuerState.is_edit_open,
                on_open_change=IssuerState.set_is_edit_open,
            ),
            width="100%",
            spacing="4",
            on_mount=IssuerState.load_issuers,
        )
    )
