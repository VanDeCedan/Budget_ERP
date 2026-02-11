import reflex as rx
from ...state.budget_state import BudgetState
from ...components.layout import layout
from ...models.ptab import Ptab

def ptab_row(ptab: Ptab) -> rx.Component:
    return rx.table.row(
        rx.table.cell(ptab.year),
        rx.table.cell(ptab.projet),
        rx.table.cell(ptab.activity_code),
        rx.table.cell(ptab.activities),
        rx.table.cell(ptab.amount.to(str)),
        rx.table.cell(
            rx.badge(
                ptab.status,
                color_scheme=rx.cond(ptab.status == "active", "green", "red"),
            )
        ),
    )

def preview_row(row: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(row["activities"]),
        rx.table.cell(row["projet_code"]),
        rx.table.cell(row["activity_code"]),
        rx.table.cell(row["amount"].to(str)),
    )

def upload_budget_form() -> rx.Component:
    return rx.vstack(
        rx.text("Enregistrer un budget", font_size="1.5em", font_weight="bold"),
        rx.cond(
            ~BudgetState.show_preview,
            # Phase 1: Upload
            rx.vstack(
                rx.select(
                    ["2026", "2025"],
                    placeholder="Année",
                    value=BudgetState.year,
                    on_change=BudgetState.set_year
                ),
                rx.select(
                    ["ARS3", "CC", "PSDSR2", "IRPB"],
                    placeholder="Projet",
                    value=BudgetState.project,
                    on_change=BudgetState.set_project
                ),
                rx.upload(
                    rx.vstack(
                        rx.button("Select File", color="white", bg="blue", margin="1em"),
                        rx.text("Drag and drop files here or click to select files"),
                    ),
                    id="upload1",
                    border="1px dotted rgb(107,99,246)",
                    padding="2em",
                ),
                rx.hstack(
                    rx.button("Annuler", on_click=BudgetState.close_upload_dialog, variant="soft", color_scheme="gray"),
                    rx.button("Aperçu", on_click=lambda: BudgetState.handle_upload(rx.upload_files(upload_id="upload1"))),
                ),
                spacing="4",
                width="100%",
            ),
            # Phase 2: Preview
            rx.vstack(
                rx.text(f"Aperçu du budget {BudgetState.project} - {BudgetState.year}", font_size="1em", color="gray"),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Activity"),
                            rx.table.column_header_cell("Project Code"),
                            rx.table.column_header_cell("Code"),
                            rx.table.column_header_cell("Amount"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(BudgetState.preview_data, preview_row)
                    ),
                    width="100%",
                ),
                rx.hstack(
                    rx.button("Retour", on_click=BudgetState.cancel_import, variant="soft", color_scheme="gray"),
                    rx.button("Confirmer l'importation", on_click=BudgetState.confirm_import, color_scheme="green"),
                ),
                max_height="400px",
                overflow_y="auto",
                spacing="4",
                width="100%",
            )
        ),
        spacing="4",
        width="100%",
    )

def delete_budget_form() -> rx.Component:
    return rx.vstack(
        rx.text("Supprimer un budget", font_size="1.5em", font_weight="bold"),
        rx.select(
            ["2026", "2025"],
            placeholder="Année",
            value=BudgetState.year,
            on_change=BudgetState.set_year
        ),
        rx.select(
            ["ARS3", "CC", "PSDSR2", "IRPB"],
            placeholder="Projet",
            value=BudgetState.project,
            on_change=BudgetState.set_project
        ),
        rx.text("Attention: Supprimer rendra toutes les activités inactives.", color="red", font_size="0.8em"),
        rx.hstack(
            rx.button("Annuler", on_click=BudgetState.close_delete_dialog, variant="soft", color_scheme="gray"),
            rx.button("Supprimer", on_click=BudgetState.delete_budget, color_scheme="red"),
        ),
        spacing="4",
    )

def budgets_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.text("Gestion du budget", font_size="2em", font_weight="bold"),
                rx.spacer(),
                rx.button("Enregistrer un budget", on_click=BudgetState.open_upload_dialog),
                rx.button("Supprimer un budget", on_click=BudgetState.open_delete_dialog, color_scheme="red", variant="outline", margin_left="2"),
                width="100%",
                align="center",
            ),
             rx.text("Lignes budgétaires actives (PTAB)", font_size="0.8em", color="gray"),
            # Filter Bar
            rx.flex(
                rx.select(
                    ["all", "2026", "2025"],
                    value=BudgetState.search_year,
                    on_change=BudgetState.set_search_year,
                    size="1",
                    width="120px"
                ),
                rx.select(
                    ["all", "ARS3", "CC", "PSDSR2", "IRPB"],
                    value=BudgetState.search_project,
                    on_change=BudgetState.set_search_project,
                    size="1",
                    width="120px"
                ),
                rx.button(
                    "Filtrer",
                    on_click=BudgetState.apply_filters,
                    size="1",
                    color_scheme="blue"
                ),
                rx.button(
                    "Reset",
                    on_click=BudgetState.reset_filters,
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
                        rx.table.column_header_cell("Année"),
                        rx.table.column_header_cell("Projet"),
                        rx.table.column_header_cell("Code"),
                        rx.table.column_header_cell("Activité"),
                        rx.table.column_header_cell("Montant"),
                        rx.table.column_header_cell("Statut"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(BudgetState.display_ptabs, ptab_row)
                ),
                width="100%",
            ),
             # Dialogs
            rx.dialog.root(
                rx.dialog.content(upload_budget_form(), size="4"),
                open=BudgetState.is_upload_open,
                on_open_change=BudgetState.set_is_upload_open,
            ),
            rx.dialog.root(
                rx.dialog.content(delete_budget_form()),
                open=BudgetState.is_delete_open,
                on_open_change=BudgetState.set_is_delete_open,
            ),
            width="100%",
            spacing="4",
            on_mount=BudgetState.load_ptabs,
        )
    )
