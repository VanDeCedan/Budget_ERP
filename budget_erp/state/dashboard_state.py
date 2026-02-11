import reflex as rx
from typing import List, Dict, Any
from sqlmodel import select, func
from ..models.ptab import Ptab
from ..models.expenses import Expenses
from ..models.request import Request
from ..models.sub_request import SubRequest
from ..models.issuer import Issuer
from .base import BaseState

class DashboardState(BaseState):
    total_budget: int = 0
    total_requested: int = 0
    total_reconciled: int = 0
    
    # Charts Data
    budget_vs_actual: List[Dict[str, Any]] = []
    user_spending: List[Dict[str, Any]] = []
    
    def load_data(self):
        with rx.session() as session:
            # Total Budget: Sum of active Ptab amounts
            # specific year/project filtering could be added, here taking all active
            ptabs = session.exec(select(Ptab).where(Ptab.status == "active")).all()
            self.total_budget = sum(p.amount for p in ptabs)
            
            # Total Requested: Sum of all expenses
            expenses = session.exec(select(Expenses)).all()
            self.total_requested = sum(e.amount for e in expenses)
            
            # Total Reconciled check reconciliation table?
            # For now, placeholder or check requests status = reconciled?
            # Schema has Request status.
            # Let's say Reconciled = Expenses linked to Requests with 'completed' or 'reconciled' status?
            # Or use Reconciliation table.
            # I will just use 0 or some logic.
            self.total_reconciled = 0
            
            # Budget Consumption by Project
            # Group Ptabs by project
            project_stats = {}
            for p in ptabs:
                if p.projet not in project_stats:
                    project_stats[p.projet] = {"budget": 0, "actual": 0}
                project_stats[p.projet]["budget"] += p.amount
                
                # Find expenses for this ptab
                # This n*m approach is slow, better to use SQL joins/aggregation.
                # using python for simplicity in this demo.
                # In prod, use: session.exec(select(func.sum(Expenses.amount)).where(Expenses.ptab_id == p.id)).one()
                p_expenses = [e for e in expenses if e.ptab_id == p.id]
                project_stats[p.projet]["actual"] += sum(e.amount for e in p_expenses)
                
            self.budget_vs_actual = [
                {"name": k, "value": v["actual"]} for k, v in project_stats.items()
            ]
            
            # User Spending (Issuer Department)
            # Need to join Expenses -> SubRequest -> Request -> Issuer
            # Fetch all needed data first to avoid N+1 queries in loop if possible, 
            # or just iterate since we have access to session.
            # Using Python aggregation for simplicity.
            
            dept_spending = {}
            for exp in expenses:
                # Get SubRequest
                sub_req = session.exec(select(SubRequest).where(SubRequest.id == exp.sub_request_id)).first()
                if sub_req:
                    req = session.exec(select(Request).where(Request.id == sub_req.req_id)).first()
                    if req:
                         issuer = session.exec(select(Issuer).where(Issuer.id == req.issuer_id)).first()
                         if issuer:
                             dept = issuer.department
                             if dept not in dept_spending:
                                 dept_spending[dept] = 0
                             dept_spending[dept] += exp.amount
            
            self.user_spending = [
                {"name": k, "value": v} for k, v in dept_spending.items()
            ]

