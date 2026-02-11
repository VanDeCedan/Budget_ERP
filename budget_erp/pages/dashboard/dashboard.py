import reflex as rx
from ...components.layout import layout
from ...state.dashboard_state import DashboardState

def stat_card(label: str, value: str, icon: str, color: str) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.icon(icon, size=32, color=color),
            rx.vstack(
                rx.text(label, font_size="0.8em", font_weight="bold", color="gray"),
                rx.text(value, font_size="1.5em", font_weight="bold"),
                spacing="1",
            ),
            align="center",
            spacing="4",
        ),
        size="2",
    )

def dashboard_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.text("Dashboard", font_size="2em", font_weight="bold"),
            
            # Stats Cards
            rx.grid(
                stat_card("Total Budget", f"${DashboardState.total_budget}", "wallet", "blue"),
                stat_card("Total Requested", f"${DashboardState.total_requested}", "banknote", "green"),
                stat_card("Total Reconciled", f"${DashboardState.total_reconciled}", "arrow-left-right", "orange"),
                columns="3",
                spacing="4",
                width="100%",
            ),
            
            rx.divider(),
            
            # Charts
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.text("Budget Consumption", font_weight="bold"),
                        rx.recharts.bar_chart(
                            rx.recharts.bar(
                                data_key="value", stroke="#8884d8", fill="#8884d8",
                            ),
                            rx.recharts.x_axis(data_key="name"),
                            rx.recharts.y_axis(),
                            data=DashboardState.budget_vs_actual,
                            height=300,
                        ),
                        width="100%",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.text("User Spending", font_weight="bold"),
                         rx.recharts.bar_chart(
                            rx.recharts.bar(
                                data_key="value", stroke="#82ca9d", fill="#82ca9d",
                            ),
                            rx.recharts.x_axis(data_key="name"),
                            rx.recharts.y_axis(),
                            data=DashboardState.user_spending,
                            height=300,
                        ),
                        width="100%",
                    ),
                ),
                columns="2",
                spacing="4",
                width="100%",
            ),
            
            spacing="6",
            width="100%",
            on_mount=DashboardState.load_data,
        )
    )
