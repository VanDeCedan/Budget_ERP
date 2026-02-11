import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlmodel import select
from ..models.request import Request
from ..models.sub_request import SubRequest
from ..models.expenses import Expenses
from ..models.issuer import Issuer
from ..models.ptab import Ptab
from ..models.balance import Balance
from ..utils.security import decrypt_data
from .base import BaseState
import pandas as pd
import io
from ..utils.balance_logic import recalculate_balances

class RequestState(BaseState):
    requests: List[dict] = []
    issuers: List[Issuer] = [] # For dropdown
    ptabs: List[Ptab] = [] # For activity codes
    
    # Form 1 Fields
    issuer_id: str = ""
    request_type: str = "Voyage" # Travel/Purchase
    object: str = ""
    
    # Form 2 Fields (Line Item)
    activity_code: str = "" # Ptab activity_code
    amount: str = ""
    
    # In-memory Lines (Dataframe)
    lines: List[Dict[str, Any]] = []
    
    # Computed Total
    total_amount: int = 0
    
    # Dialog control
    is_dialog_open: bool = False
    show_preview: bool = False
    is_complementary: bool = False
    selected_initial_id: str = "" # stores "ID: Object" selected
    comp_filter_issuer: str = "" # Filter for complementary requests
    
    # Filter fields
    filter_issuer: str = "all"
    filter_object: str = ""
    filter_status: str = "all"
    applied_filter_issuer: str = "all"
    applied_filter_object: str = ""
    applied_filter_status: str = "all"
    
    def load_data(self):
        with rx.session() as session:
            # Shift focus to SubRequests as the primary table entries
            db_sub_requests = session.exec(select(SubRequest).order_by(SubRequest.register_at.desc())).all()
            self.requests = []
            
            for sub_req in db_sub_requests:
                item_dict = sub_req.dict()
                
                # 1. Get Request and Issuer Info
                req = session.exec(select(Request).where(Request.id == sub_req.req_id)).first()
                if req:
                    issuer = session.exec(select(Issuer).where(Issuer.id == req.issuer_id)).first()
                    if issuer:
                        try:
                            item_dict["issuer_name"] = decrypt_data(issuer.name)
                        except:
                            item_dict["issuer_name"] = "Error Decrypting"
                    else:
                        item_dict["issuer_name"] = "Unknown Issuer"
                else:
                    item_dict["issuer_name"] = "No Parent Request"
                
                # 2. Calculate Total Amount for this specific SubRequest
                expenses = session.exec(select(Expenses).where(Expenses.sub_request_id == sub_req.id)).all()
                item_dict["total_amount"] = sum(e.amount for e in expenses)
                
                # 3. Add Mapped Type for Display
                raw_type = item_dict.get("sub_request_type", "initial")
                item_dict["display_type"] = "Complément" if raw_type == "add" else "Initial"
                
                # 4. Format Date
                if sub_req.register_at:
                    item_dict["date"] = sub_req.register_at.strftime("%Y-%m-%d")
                else:
                    item_dict["date"] = "N/A"
                
                self.requests.append(item_dict)

            self.issuers = session.exec(select(Issuer).where(Issuer.status == "active")).all()
            self.ptabs = session.exec(select(Ptab).where(Ptab.status == "active")).all()

    @rx.var
    def display_requests(self) -> List[dict]:
        filtered = []
        for req in self.requests:
            # Issuer Filter
            if self.applied_filter_issuer != "all" and req.get("issuer_name") != self.applied_filter_issuer:
                continue
            
            # Object Filter
            if self.applied_filter_object and self.applied_filter_object not in req.get("object", "").lower():
                continue
                
            # Status Filter
            if self.applied_filter_status != "all" and req.get("status") != self.applied_filter_status:
                continue
                
            filtered.append(req)
        return filtered

    @rx.var
    def issuer_options(self) -> List[str]:
        options = []
        for i in self.issuers:
            try:
                name = decrypt_data(i.name)
                options.append(name)
            except:
                options.append("Error Decrypting")
        return options

    @rx.var
    def table_filter_issuer_options(self) -> List[str]:
        return ["all"] + self.issuer_options

    @rx.var
    def initial_sub_request_options(self) -> List[str]:
        # Returns list of active sub-requests for dropdown as "Object"
        with rx.session() as session:
            query = select(SubRequest).where(SubRequest.status == "active")
            
            if self.comp_filter_issuer:
                # Find issuer_id
                target_issuer_id = None
                for i in self.issuers:
                    try:
                        if decrypt_data(i.name) == self.comp_filter_issuer:
                            target_issuer_id = i.id
                            break
                    except:
                        continue
                
                if target_issuer_id:
                    # Filter sub_requests by joined request issuer
                    query = query.join(Request).where(Request.issuer_id == target_issuer_id)
                else:
                    # If issuer selected but not found (unlikely), return empty
                    return []

            results = session.exec(query).all()
            return [sr.object for sr in results if sr.object]

    @rx.var
    def ptab_options(self) -> List[str]:
        return [str(p.activity_code) for p in self.ptabs]

    def set_issuer_id(self, value: str):
        self.issuer_id = value

    def set_request_type(self, value: str):
        self.request_type = value

    def set_object(self, value: str):
        self.object = value

    def set_activity_code(self, value: str):
        self.activity_code = value

    def set_amount(self, value: str):
        self.amount = value

    def set_selected_initial_id(self, value: str):
        self.selected_initial_id = value

    def set_comp_filter_issuer(self, value: str):
        self.comp_filter_issuer = value

    def set_filter_issuer(self, value: str):
        self.filter_issuer = value

    def set_filter_object(self, value: str):
        self.filter_object = value

    def set_filter_status(self, value: str):
        self.filter_status = value

    def apply_table_filters(self):
        self.applied_filter_issuer = self.filter_issuer
        self.applied_filter_object = self.filter_object.lower()
        self.applied_filter_status = self.filter_status

    def reset_table_filters(self):
        self.filter_issuer = "all"
        self.filter_object = ""
        self.filter_status = "all"
        self.applied_filter_issuer = "all"
        self.applied_filter_object = ""
        self.applied_filter_status = "all"

    def set_is_dialog_open(self, value: bool):
        self.is_dialog_open = value

    def open_dialog(self, is_comp: bool = False):
        self.is_dialog_open = True
        self.show_preview = False
        self.is_complementary = is_comp
        self.selected_initial_id = ""
        self.issuer_id = ""
        self.request_type = "Voyage"
        self.object = ""
        self.activity_code = ""
        self.amount = ""
        self.lines = []
        self.total_amount = 0
        self.comp_filter_issuer = ""

    def close_dialog(self):
        self.is_dialog_open = False
        self.show_preview = False

    def open_preview(self):
        if self.is_complementary:
            if not self.selected_initial_id or not self.object:
                return rx.window_alert("Please select an initial request and enter an object.")
        else:
            if not self.issuer_id or not self.request_type or not self.object:
                 return rx.window_alert("Please fill General Information.")
        
        if not self.lines:
             return rx.window_alert("Please add at least one line item.")
        self.show_preview = True

    def cancel_preview(self):
        self.show_preview = False

    def set_amount(self, value: str):
        self.amount = value

    def add_line(self):
        try:
            amount_val = int(self.amount)
        except:
            return rx.window_alert("Invalid amount.")

        if not self.activity_code or amount_val <= 0:
            return rx.window_alert("Invalid code or amount.")
        
        # Verify code exists
        # In integer conversion
        try:
            code = int(self.activity_code)
        except:
             return rx.window_alert("Invalid code format.")
             
        # Check if code is valid in ptabs
        valid = False
        for p in self.ptabs:
            if p.activity_code == code:
                valid = True
                break
        if not valid:
             return rx.window_alert("Activity code not found.")

        # Budget Coverage Check
        with rx.session() as session:
            # 1. Find PTAB ID for this code
            ptab = session.exec(select(Ptab).where(Ptab.activity_code == code, Ptab.status == "active")).first()
            if not ptab:
                return rx.window_alert("Could not find active budget line for this code.")
            
            # 2. Get Balance
            balance = session.exec(select(Balance).where(Balance.ptab_id == ptab.id)).first()
            available = balance.amount if balance else 0
            
            # 3. Validation
            if amount_val > available:
                return rx.window_alert(
                    f"Montant insuffisant !\n"
                    f"Disponible : {available:,}\n"
                    f"Saisi : {amount_val:,}"
                )

        self.lines.append({
            "activity_code": code,
            "amount": amount_val
        })
        self.calculate_total()
        self.activity_code = "" # Reset
        self.amount = ""

    def remove_line(self, index: int):
        if 0 <= index < len(self.lines):
            self.lines.pop(index)
            self.calculate_total()

    def calculate_total(self):
        self.total_amount = sum(line["amount"] for line in self.lines)

    def save_request(self):
        if self.is_complementary:
            if not self.selected_initial_id or not self.object:
                return rx.window_alert("Missing initial request or object.")
        else:
            if not self.issuer_id or not self.request_type or not self.object:
                return rx.window_alert("Please fill General Information.")
        
        if not self.lines:
             return rx.window_alert("Please add at least one line item.")
             
        created_by_id = self.current_user.id if self.current_user else 1
             
        with rx.session() as session:
            try:
                actual_req_id = None
                if self.is_complementary:
                    # Find by Object name as requested by user
                    try:
                        sr_parent = session.exec(
                            select(SubRequest).where(
                                SubRequest.object == self.selected_initial_id,
                                SubRequest.status == "active"
                            )
                        ).first()
                        if not sr_parent:
                            return rx.window_alert("Selected initial request not found.")
                        actual_req_id = sr_parent.req_id
                    except:
                        return rx.window_alert("Invalid selection for initial request.")
                else:
                    # 1. Create New Request
                    # Find issuer_id by matching name
                    actual_issuer_id = None
                    for i in self.issuers:
                        try:
                            if decrypt_data(i.name) == self.issuer_id:
                                actual_issuer_id = i.id
                                break
                        except:
                            continue
                    
                    if actual_issuer_id is None:
                        return rx.window_alert("Invalid Issuer Selection")

                    req = Request(
                        issuer_id=actual_issuer_id,
                        request_type=self.request_type,
                        status="active"
                    )
                    session.add(req)
                    session.flush() # get ID
                    actual_req_id = req.id
                
                # 2. Create SubRequest
                sub_req = SubRequest(
                    req_id=actual_req_id,
                    sub_request_type="add" if self.is_complementary else "initial",
                    object=self.object,
                    status="active",
                    register_by=created_by_id
                )
                session.add(sub_req)
                session.flush() # get ID
                
                # 2.5 Create Travel if NEW request and type is Voyage
                if not self.is_complementary and self.request_type == "Voyage":
                    from ..models.travel import Travel
                    travel = Travel(
                        sub_request_id=sub_req.id,
                        travel_type="advance" 
                    )
                    session.add(travel)

                
                # 3. Create Expenses
                for line in self.lines:
                    # Find ptab_id from activity_code
                    # We know code is valid from add_line, but need ID now.
                    # Efficient way: query or lookup. 
                    # querying inside loop is okay for small N.
                    code = line["activity_code"]
                    ptab = session.exec(select(Ptab).where(Ptab.activity_code == code)).first()
                    if ptab:
                        exp = Expenses(
                            ptab_id=ptab.id,
                            sub_request_id=sub_req.id,
                            amount=line["amount"]
                        )
                        session.add(exp)
                    else:
                        raise Exception(f"Ptab code {code} not found during save.")
                
                recalculate_balances(session)
                session.commit()
                self.load_data()
                self.close_dialog()
                return rx.window_alert("Request registered successfully.")
                
            except Exception as e:
                session.rollback()
                return rx.window_alert(f"Error saving request: {str(e)}")

    def cancel_request_action(self, sub_req: dict):
        with rx.session() as session:
            sr = session.exec(select(SubRequest).where(SubRequest.id == sub_req["id"])).first()
            if sr:
                sr.status = "canceled"
                session.add(sr)
                recalculate_balances(session)
                session.commit()
                self.load_data()

    def download_requests_excel(self):
        """Generates an Excel file from the filtered requests data."""
        if not self.display_requests:
            return rx.window_alert("Aucune donnée à télécharger.")
            
        df = pd.DataFrame(self.display_requests)
        # Rename columns for clarity in Excel
        column_mapping = {
            "date": "Date",
            "issuer_name": "Demandeur",
            "display_type": "Type",
            "object": "Objet",
            "total_amount": "Montant Total",
            "status": "Statut"
        }
        # Drop columns not needed in Excel
        df = df[[col for col in column_mapping.keys() if col in df.columns]]
        df = df.rename(columns=column_mapping)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output) as writer:
            df.to_excel(writer, index=False, sheet_name='Requêtes')
        
        filename = f"requetes_budgetaires_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return rx.download(
            data=output.getvalue(),
            filename=filename
        )
