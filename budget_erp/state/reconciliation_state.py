import reflex as rx
from typing import List, Dict, Any, Optional
from sqlmodel import select
from ..models.reconciliation import Reconciliation
from ..models.regularisation import Regularisation
from ..models.request import Request
from ..models.sub_request import SubRequest
from ..models.expenses import Expenses
from ..models.issuer import Issuer
from ..models.ptab import Ptab
from ..utils.security import decrypt_data
from .base import BaseState
from ..utils.balance_logic import recalculate_balances

class ReconciliationState(BaseState):
    reconciliations: List[dict] = []
    issuers: List[Issuer] = []
    
    # Form fields - Phase 1
    type_recon: str = "advance" # advance/momo/facture
    issuer_name: str = ""
    selected_object: str = ""
    
    # Phase 2
    expense_lines: List[Dict[str, Any]] = []
    show_lines: bool = False # Toggle between Phase 1 and Phase 2
    
    # Dialog control
    is_dialog_open: bool = False
    
    def load_data(self):
        with rx.session() as session:
            db_reconciliations = session.exec(select(Reconciliation).order_by(Reconciliation.register_at.desc())).all()
            self.reconciliations = []
            for recon in db_reconciliations:
                recon_dict = recon.dict()
                # Get request info
                req = session.exec(select(Request).where(Request.id == recon.req_id)).first()
                if req:
                    issuer = session.exec(select(Issuer).where(Issuer.id == req.issuer_id)).first()
                    recon_dict["issuer_name"] = decrypt_data(issuer.name) if issuer else "Unknown"
                
                # Calculate Total Amount from Regularisations
                regs = session.exec(select(Regularisation).where(Regularisation.reconci_id == recon.id)).all()
                recon_dict["total_amount"] = sum(r.amount for r in regs)
                
                self.reconciliations.append(recon_dict)
                
            self.issuers = session.exec(select(Issuer).where(Issuer.status == "active")).all()

    @rx.var
    def issuer_options(self) -> List[str]:
        options = []
        for i in self.issuers:
            try:
                options.append(decrypt_data(i.name))
            except:
                options.append("Error Decrypting")
        return options

    @rx.var
    def object_options(self) -> List[str]:
        if not self.issuer_name:
            return []
        
        try:
            with rx.session() as session:
                # 1. Find Issuer ID
                actual_issuer_id = None
                for i in self.issuers:
                    try:
                        if decrypt_data(i.name) == self.issuer_name:
                            actual_issuer_id = i.id
                            break
                    except:
                        continue
                
                if not actual_issuer_id:
                    return []
                    
                # 2. Get Requests for this Issuer
                requests = session.exec(select(Request).where(Request.issuer_id == actual_issuer_id)).all()
                if not requests:
                    return []
                    
                req_ids = [r.id for r in requests]
                
                # 3. Get Initial SubRequests for these Requests
                sub_requests = session.exec(
                    select(SubRequest).where(
                        SubRequest.req_id.in_(req_ids),
                        SubRequest.sub_request_type == "initial",
                        SubRequest.status == "active"
                    )
                ).all()
                
                return [sr.object for sr in sub_requests if sr.object]
        except Exception:
            return []

    def set_type_recon(self, value: str):
        self.type_recon = value

    def set_issuer_name(self, value: str):
        self.issuer_name = value
        self.selected_object = "" # Reset object when issuer changes

    def set_selected_object(self, value: str):
        self.selected_object = value

    def set_is_dialog_open(self, value: bool):
        self.is_dialog_open = value

    def open_dialog(self):
        self.is_dialog_open = True
        self.show_lines = False
        self.type_recon = "advance"
        self.issuer_name = ""
        self.selected_object = ""
        self.expense_lines = []

    def close_dialog(self):
        self.is_dialog_open = False

    def next_step(self):
        if not self.type_recon or not self.issuer_name or not self.selected_object:
            return rx.window_alert("Please fill all fields.")
            
        with rx.session() as session:
            # Load expense lines for selected object
            sr = session.exec(select(SubRequest).where(SubRequest.object == self.selected_object, SubRequest.status == "active")).first()
            if not sr:
                return rx.window_alert("Selected object not found.")
            
            expenses = session.exec(select(Expenses).where(Expenses.sub_request_id == sr.id)).all()
            self.expense_lines = []
            for exp in expenses:
                ptab = session.exec(select(Ptab).where(Ptab.id == exp.ptab_id)).first()
                self.expense_lines.append({
                    "id": exp.id,
                    "activity_code": ptab.activity_code if ptab else "Unknown",
                    "original_amount": exp.amount,
                    "amount_spent": 0
                })
        
        self.show_lines = True

    def prev_step(self):
        self.show_lines = False

    def update_spent_amount(self, index: int, value: str):
        try:
            val = int(value) if value else 0
            self.expense_lines[index]["amount_spent"] = val
        except:
            pass

    def add_reconciliation(self):
        # Filter lines where amount spent > 0
        valid_lines = [line for line in self.expense_lines if line["amount_spent"] > 0]
        if not valid_lines:
            return rx.window_alert("Please enter amount spent for at least one line.")
            
        created_by_id = self.current_user.id if self.current_user else 1
        
        with rx.session() as session:
            try:
                # 1. Get Request ID from SubRequest
                sr = session.exec(select(SubRequest).where(SubRequest.object == self.selected_object, SubRequest.status == "active")).first()
                if not sr:
                    return rx.window_alert("Error retrieving source request.")
                
                # 2. Create Reconciliation
                recon = Reconciliation(
                    req_id=sr.req_id,
                    reconci_type=self.type_recon,
                    status="active",
                    register_by=created_by_id
                )
                session.add(recon)
                session.flush() # get ID
                
                # 3. Create Regularisations
                for line in valid_lines:
                    reg = Regularisation(
                        expenses_id=line["id"],
                        reconci_id=recon.id,
                        amount=line["amount_spent"]
                    )
                    session.add(reg)
                
                recalculate_balances(session)
                session.commit()
                self.load_data()
                self.close_dialog()
                return rx.window_alert("Reconciliation registered successfully.")
            except Exception as e:
                session.rollback()
                return rx.window_alert(f"Error: {str(e)}")
            
    def cancel_reconciliation(self, recon_dict: dict):
        with rx.session() as session:
            recon = session.exec(select(Reconciliation).where(Reconciliation.id == recon_dict["id"])).first()
            if recon:
                recon.status = "canceled"
                session.add(recon)
                recalculate_balances(session)
                session.commit()
                self.load_data()
