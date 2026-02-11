import reflex as rx
from . import models
from .pages.dashboard.dashboard import dashboard_page
from .pages.users.users import users_page
from .pages.issuers.issuers import issuers_page
from .pages.budgets.budgets import budgets_page
from .pages.requests.requests import requests_page
from .pages.reconciliations.reconciliations import reconciliations_page
from .pages.solde.solde import solde_page

from .pages.login import login_page
from .state.auth_state import AuthState
from .state.base import BaseState

def index() -> rx.Component:
    return dashboard_page()

app = rx.App()
app.add_page(index, route="/", on_load=BaseState.check_login)
app.add_page(login_page, route="/login")
app.add_page(users_page, route="/users", on_load=[BaseState.check_login, AuthState.check_admin])
app.add_page(issuers_page, route="/issuers", on_load=BaseState.check_login)
app.add_page(budgets_page, route="/budgets", on_load=BaseState.check_login)
app.add_page(requests_page, route="/requests", on_load=BaseState.check_login)
app.add_page(reconciliations_page, route="/reconciliations", on_load=BaseState.check_login)
app.add_page(solde_page, route="/solde", on_load=BaseState.check_login)
