import reflex as rx
from ...state.reconciliation_state import ReconciliationState
from ...components.layout import layout
from ...models.reconciliation import Reconciliation

def reconciliation_row(recon: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(recon["issuer_name"]),
        rx.table.cell(recon["reconci_type"]),
        rx.table.cell(f"{recon['total_amount']:,}"),
        rx.table.cell(
            rx.badge(
                recon["status"],
                color_scheme=rx.cond(recon["status"] == "active", "green", "red"),
            )
        ),
        rx.table.cell(
            rx.cond(
                recon["status"] == "active",
                rx.button(
                    "Annuler", 
                    on_click=lambda: ReconciliationState.cancel_reconciliation(recon),
                    color_scheme="red",
                    variant="surface"
                ),
                rx.text("-"),
            )
        ),
    )

def expense_line_row(line: dict, index: int) -> rx.Component:
    return rx.table.row(
        rx.table.cell(line["activity_code"], font_size="0.8em"),
        rx.table.cell(f"{line['original_amount']:,}", font_size="0.8em"),
        rx.table.cell(
            rx.input(
                placeholder="Montant dépensé",
                type="number",
                value=line["amount_spent"].to(str),
                on_change=lambda val: ReconciliationState.update_spent_amount(index, val),
                size="1",
                width="150px"
            )
        ),
    )

def reconciliation_form() -> rx.Component:
    return rx.cond(
        ~ReconciliationState.show_lines,
        # Step 1: Selection
        rx.vstack(
            rx.text("Informations de base", font_size="0.9em", font_weight="bold", color="gray"),
            rx.select(
                ["advance", "momo", "facture"],
                placeholder="Type",
                value=ReconciliationState.type_recon,
                on_change=ReconciliationState.set_type_recon,
                width="100%",
                size="1"
            ),
            rx.select(
                ReconciliationState.issuer_options,
                placeholder="Demandeur (Issuer)",
                value=ReconciliationState.issuer_name,
                on_change=ReconciliationState.set_issuer_name,
                width="100%",
                size="1"
            ),
            rx.select(
                ReconciliationState.object_options,
                placeholder="Objet de la requête",
                value=ReconciliationState.selected_object,
                on_change=ReconciliationState.set_selected_object,
                width="100%",
                size="1"
            ),
            rx.divider(),
            rx.hstack(
                rx.button("Annuler", on_click=ReconciliationState.close_dialog, variant="soft", color_scheme="gray"),
                rx.button("Suivant", on_click=ReconciliationState.next_step, color_scheme="blue"),
                width="100%",
                justify="end",
            ),
            spacing="3",
            width="100%",
        ),
        # Step 2: Lines
        rx.vstack(
            rx.text("Régularisation des lignes", font_size="0.9em", font_weight="bold", color="gray"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Code", font_size="0.8em"),
                        rx.table.column_header_cell("Initiale", font_size="0.8em"),
                        rx.table.column_header_cell("Dépensé", font_size="0.8em"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(ReconciliationState.expense_lines, lambda line, i: expense_line_row(line, i))
                ),
                width="100%",
            ),
            rx.divider(),
            rx.hstack(
                rx.button("Précédent", on_click=ReconciliationState.prev_step, variant="soft", color_scheme="gray"),
                rx.button("Enregistrer", on_click=ReconciliationState.add_reconciliation, color_scheme="green"),
                width="100%",
                justify="end",
            ),
            spacing="3",
            width="100%",
        )
    )

def reconciliations_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.text("Gestion des réconciliations", font_size="2em", font_weight="bold"),
                rx.spacer(),
                rx.button("Enregistrer", on_click=ReconciliationState.open_dialog),
                width="100%",
                align="center",
            ),
             rx.text("Liste des Reconciliations", font_size="0.8em", color="gray"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Demandeur"),
                        rx.table.column_header_cell("Type"),
                        rx.table.column_header_cell("Montant"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Actions"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(ReconciliationState.reconciliations, reconciliation_row)
                ),
                width="100%",
            ),
             # Dialog
            rx.dialog.root(
                rx.dialog.content(reconciliation_form()),
                open=ReconciliationState.is_dialog_open,
                on_open_change=ReconciliationState.set_is_dialog_open,
            ),
            width="100%",
            spacing="4",
            on_mount=ReconciliationState.load_data,
        )
    )
