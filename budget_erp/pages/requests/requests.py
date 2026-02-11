import reflex as rx
from ...state.request_state import RequestState
from ...components.layout import layout
from .common import request_row, line_item_row, request_form


def requests_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.text("Gestion des requetes", font_size="2em", font_weight="bold"),
                rx.spacer(),
                rx.button("Nouvelle requête", on_click=lambda: RequestState.open_dialog(False)),
                rx.button("Requête complémentaire", on_click=lambda: RequestState.open_dialog(True), color_scheme="blue", variant="surface"),
                width="100%",
                align="center",
            ),
             rx.text("Listes des requêtes", font_size="0.8em", color="gray"),
            # Filter Bar
            rx.flex(
                rx.select(
                    RequestState.table_filter_issuer_options,
                    value=RequestState.filter_issuer,
                    on_change=RequestState.set_filter_issuer,
                    size="1",
                    width="200px"
                ),
                rx.input(
                    placeholder="Filtrer par objet...",
                    value=RequestState.filter_object,
                    on_change=RequestState.set_filter_object,
                    size="1",
                    width="250px"
                ),
                rx.select(
                   ["all", "active", "canceled"],
                    value=RequestState.filter_status,
                    on_change=RequestState.set_filter_status,
                    size="1",
                    width="120px"
                ),
                rx.button(
                    "Filtrer",
                    on_click=RequestState.apply_table_filters,
                    size="1",
                    color_scheme="blue"
                ),
                rx.button(
                    "Reset",
                    on_click=RequestState.reset_table_filters,
                    size="1",
                    variant="soft",
                    color_scheme="gray"
                ),
                rx.spacer(),
                rx.button(
                    "Télécharger",
                    on_click=RequestState.download_requests_excel,
                    size="1",
                    color_scheme="green",
                    variant="outline",
                    left_icon="download",
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
                        rx.table.column_header_cell("Date"),
                        rx.table.column_header_cell("Demandeur"),
                        rx.table.column_header_cell("Type"),
                        rx.table.column_header_cell("Objet"),
                        rx.table.column_header_cell("Montant Total"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Actions"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(RequestState.display_requests, request_row)
                ),
                width="100%",
            ),
             # Dialog
            rx.dialog.root(
                rx.dialog.content(request_form(), max_width="800px"),
                open=RequestState.is_dialog_open,
                on_open_change=RequestState.set_is_dialog_open,
            ),
            width="100%",
            spacing="4",
            on_mount=RequestState.load_data,
        )
    )
