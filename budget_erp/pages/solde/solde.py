import reflex as rx
from ...state.solde_state import SoldeState
from ...components.layout import layout

def solde_row(data: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(data["year"]),
        rx.table.cell(data["project"]),
        rx.table.cell(data["project_code"]),
        rx.table.cell(data["item_code"]),
        rx.table.cell(data["activity_code"]),
        rx.table.cell(f"{data['baseline_amount']:,}"),
        rx.table.cell(
            rx.text(
                f"{data['balance']:,}",
                color=rx.cond(data["is_negative"], "red", "green"),
                font_weight="bold"
            )
        ),
    )

def solde_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.text("État des Soldes Budgétaires", font_size="2em", font_weight="bold"),
                rx.spacer(),
                width="100%",
                align="center",
            ),
            rx.text("Comparaison entre le budget initial (Ptab) et le solde actuel.", font_size="0.8em", color="gray"),
            
            # Filter Bar
            rx.flex(
                rx.select(
                    ["all", "2026", "2025"],
                    value=SoldeState.filter_year,
                    on_change=SoldeState.set_filter_year,
                    size="1",
                    width="120px"
                ),
                rx.select(
                    ["all", "ARS3", "CC", "PSDSR2", "IRPB"],
                    value=SoldeState.filter_project,
                    on_change=SoldeState.set_filter_project,
                    size="1",
                    width="120px"
                ),
                rx.input(
                    placeholder="Code Activité...",
                    value=SoldeState.filter_activity_code,
                    on_change=SoldeState.set_filter_activity_code,
                    size="1",
                    width="150px"
                ),
                rx.button(
                    "Filtrer",
                    on_click=SoldeState.apply_table_filters,
                    size="1",
                    color_scheme="blue"
                ),
                rx.button(
                    "Reset",
                    on_click=SoldeState.reset_table_filters,
                    size="1",
                    variant="soft",
                    color_scheme="gray"
                ),
                rx.spacer(),
                rx.button(
                    "Télécharger",
                    on_click=SoldeState.download_solde_excel,
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
                        rx.table.column_header_cell("Année"),
                        rx.table.column_header_cell("Projet"),
                        rx.table.column_header_cell("Code Projet"),
                        rx.table.column_header_cell("Code Item"),
                        rx.table.column_header_cell("Code Activité"),
                        rx.table.column_header_cell("Budget Initial"),
                        rx.table.column_header_cell("Solde Actuel"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(SoldeState.display_solde, solde_row)
                ),
                width="100%",
                variant="surface",
            ),
            width="100%",
            spacing="4",
            on_mount=SoldeState.load_solde,
        )
    )
