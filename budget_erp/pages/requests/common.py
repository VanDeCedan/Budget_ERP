import reflex as rx
from ...state.request_state import RequestState
from .new_request import new_request_form_content
from .complementary_request import complementary_request_form_content

def request_row(req: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(req["date"]),
        rx.table.cell(req["issuer_name"]),
        rx.table.cell(req["display_type"]),
        rx.table.cell(req["object"]),
        rx.table.cell(f"{req['total_amount']:,}"),
        rx.table.cell(
            rx.badge(
                req["status"],
                color_scheme=rx.cond(
                    req["status"] == "active", "green",
                    rx.cond(req["status"] == "completed", "blue", "red")
                ),
            )
        ),
        rx.table.cell(
            rx.cond(
                req["status"] == "active",
                rx.button(
                    "Annuler", 
                    on_click=lambda: RequestState.cancel_request_action(req),
                    color_scheme="red",
                    variant="surface"
                ),
                rx.text("-"),
            )
        ),
    )

def line_item_row(line: dict, index: int) -> rx.Component:
    return rx.table.row(
        rx.table.cell(line["activity_code"], font_size="0.8em"),
        rx.table.cell(f"{line['amount']:,}", font_size="0.8em"),
        rx.table.cell(
            rx.button("X", on_click=lambda: RequestState.remove_line(index), color_scheme="red", size="1"),
            padding="1"
        ),
    )

def request_form() -> rx.Component:
    return rx.vstack(
        rx.cond(
            ~RequestState.show_preview,
            # Phase 1: Modification/Saisie
            rx.vstack(
                # Form 1 - Dynamic Content based on Initial vs Complementary
                rx.card(
                    rx.cond(
                        ~RequestState.is_complementary,
                        new_request_form_content(),
                        complementary_request_form_content()
                    ),
                    width="100%",
                    padding="2",
                ),
                # Form 2 - Budget Lines (Common)
                rx.card(
                    rx.vstack(
                        rx.text("Lignes Budgétaires", font_size="0.8em", font_weight="bold", color="gray"),
                        rx.hstack(
                            rx.select(
                                RequestState.ptab_options,
                                placeholder="Code Activité",
                                value=RequestState.activity_code,
                                on_change=RequestState.set_activity_code,
                                width="50%",
                                size="1"
                            ),
                            rx.input(
                                placeholder="Montant", 
                                type="number", 
                                value=RequestState.amount, 
                                on_change=RequestState.set_amount,
                                width="30%",
                                size="1"
                            ),
                            rx.button("Ajouter", on_click=RequestState.add_line, width="20%", size="1"),
                            width="100%",
                        ),
                        # Lines Table
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Code", font_size="0.8em"),
                                    rx.table.column_header_cell("Montant", font_size="0.8em"),
                                    rx.table.column_header_cell(""),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(RequestState.lines, lambda item, i: line_item_row(item, i))
                            ),
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text("Total:", font_weight="bold", font_size="0.9em"),
                            rx.text(f"{RequestState.total_amount}", font_weight="bold", color="blue", font_size="0.9em"),
                            align="center",
                            justify="end",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    width="100%",
                    padding="2",
                ),
                rx.hstack(
                    rx.button("Annuler", on_click=RequestState.close_dialog, variant="soft", color_scheme="gray"),
                    rx.button("Aperçu", on_click=RequestState.open_preview, color_scheme="blue"),
                    width="100%",
                    justify="end",
                ),
                width="100%",
                spacing="3",
            ),
            # Phase 2: Aperçu
            rx.vstack(
                rx.card(
                    rx.vstack(
                        rx.cond(
                            ~RequestState.is_complementary,
                            rx.hstack(
                                rx.text("Demandeur:", font_weight="bold", font_size="0.8em", width="30%"),
                                rx.text(RequestState.issuer_id, font_size="0.8em"),
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text("Requête Initiale:", font_weight="bold", font_size="0.8em", width="30%"),
                                rx.text(RequestState.selected_initial_id.to(str), font_size="0.8em"), 
                                width="100%",
                            ),
                        ),
                        rx.cond(
                            ~RequestState.is_complementary,
                            rx.hstack(
                                rx.text("Type:", font_weight="bold", font_size="0.8em", width="30%"),
                                rx.text(RequestState.request_type, font_size="0.8em"),
                                width="100%",
                            ),
                        ),
                        rx.hstack(
                            rx.text("Objet:", font_weight="bold", font_size="0.8em", width="30%"),
                            rx.text(RequestState.object, font_size="0.8em"),
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    width="100%",
                    variant="ghost",
                ),
                rx.divider(),
                rx.hstack(
                    rx.text("Montant de la requete :", font_weight="bold", font_size="1em"),
                    rx.text(f"{RequestState.total_amount:,}", font_weight="bold", color="blue", font_size="1em"),
                    width="100%",
                    justify="center",
                    padding_y="2",
                    bg="gray.50",
                    border_radius="md",
                ),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Code Activité", font_size="0.8em"),
                            rx.table.column_header_cell("Montant", font_size="0.8em"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(RequestState.lines, lambda line: rx.table.row(
                            rx.table.cell(line["activity_code"], font_size="0.8em"),
                            rx.table.cell(line["amount"].to(str), font_size="0.8em"),
                        ))
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.button("Retour", on_click=RequestState.cancel_preview, variant="soft", color_scheme="gray"),
                    rx.button("Confirmer l'enregistrement", on_click=RequestState.save_request, color_scheme="green"),
                    width="100%",
                    justify="end",
                ),
                width="100%",
                spacing="4",
            )
        ),
        spacing="4",
        max_height="85vh",
        overflow_y="auto",
        width="100%",
    )
