import reflex as rx
from typing import List, Optional
from sqlmodel import select
from ..models.issuer import Issuer
from ..utils.security import encrypt_data, decrypt_data, get_password_hash
from .base import BaseState

class IssuerState(BaseState):
    issuers: List[dict] = []
    
    # Form fields
    name: str = "" # Encrypted in DB
    department: str = "" 
    # we need to store name_index separately but it's derived from name
    
    # Dialog control
    is_add_open: bool = False
    is_edit_open: bool = False
    current_issuer_id: Optional[int] = None
    
    selected_issuer: Optional[Issuer] = None

    # Filter fields
    search_name: str = ""
    search_dept: str = "all"
    search_status: str = "all"
    applied_name: str = ""
    applied_dept: str = "all"
    applied_status: str = "all"

    def set_department(self, value: str):
        self.department = value

    def set_is_add_open(self, value: bool):
        self.is_add_open = value

    def set_is_edit_open(self, value: bool):
        self.is_edit_open = value

    def set_name(self, value: str):
        self.name = value

    def set_search_name(self, value: str):
        self.search_name = value

    def set_search_dept(self, value: str):
        self.search_dept = value

    def set_search_status(self, value: str):
        self.search_status = value

    def apply_filters(self):
        self.applied_name = self.search_name.lower()
        self.applied_dept = self.search_dept
        self.applied_status = self.search_status

    def reset_filters(self):
        self.search_name = ""
        self.search_dept = "all"
        self.search_status = "all"
        self.applied_name = ""
        self.applied_dept = "all"
        self.applied_status = "all"
    
    def load_issuers(self):
        with rx.session() as session:
            results = session.exec(select(Issuer)).all()
            self.issuers = []
            for i in results:
                issuer_dict = i.dict()
                try:
                    issuer_dict["name"] = decrypt_data(i.name)
                except:
                    issuer_dict["name"] = "Error Decrypting"
                self.issuers.append(issuer_dict)

    @rx.var
    def display_issuers(self) -> List[dict]:
        display_list = []
        for i in self.issuers:
            # Name Filter
            if self.applied_name and self.applied_name not in i["name"].lower():
                continue
            # Dept Filter
            if self.applied_dept != "all" and i["department"] != self.applied_dept:
                continue
            # Status Filter
            if self.applied_status != "all" and i["status"] != self.applied_status:
                continue
            display_list.append(i)
        return display_list
            
    def open_add_dialog(self):
        self.is_add_open = True
        self.name = ""
        self.department = ""
            
    def close_add_dialog(self):
        self.is_add_open = False
        
    def open_edit_dialog(self, issuer: dict):
        self.selected_issuer = issuer
        self.is_edit_open = True
        # Decrypt
        self.name = issuer["name"]
        self.department = issuer["department"]

    def close_edit_dialog(self):
        self.is_edit_open = False
        self.selected_issuer = None
        
    def add_issuer(self):
        with rx.session() as session:
            # Hash name for indexing/search
            name_index = get_password_hash(self.name)
            
            created_by_id = self.current_user.id if self.current_user else 1
            
            issuer = Issuer(
                name=encrypt_data(self.name), 
                name_index=name_index,
                department=self.department, 
                created_by=created_by_id,
                status="active"
            )
            session.add(issuer)
            session.commit()
            self.load_issuers()
        self.close_add_dialog()
        return rx.window_alert("Issuer registered.")

    def update_issuer(self):
        with rx.session() as session:
            if self.selected_issuer:
                issuer_id = self.selected_issuer["id"] if isinstance(self.selected_issuer, dict) else self.selected_issuer.id
                issuer = session.exec(select(Issuer).where(Issuer.id == issuer_id)).first()
                if issuer:
                    # Update department only as per requirement "Modify ... department that we will modify"
                    # What about name? "inspire you from same from users ... but here, it will department that we will modify"
                    # I'll allow modifying department. Name modification implies re-encrypting and re-hashing.
                    # Since user specifically mentioned department, I'll stick to that, but if I want to be nice I'd allow name too.
                    # Strict interpretation: only department. But let's allow name too for completeness if user changes it.
                    # But the requirement says "it will department that we will modify".
                    # I'll stick to Department only to be safe/strict, or maybe allow both.
                    # "Inspire you from same from users... but here it will department". 
                    # Users modify was Role. So here it's Department. Name is likely immutable or separate.
                    # I will allow Department modify only.
                    issuer.department = self.department
                    session.add(issuer)
                    session.commit()
                    self.load_issuers()
        self.close_edit_dialog()
        return rx.window_alert("Issuer updated.")

    def delete_issuer(self, issuer: dict):
        # Soft delete (Deactivate)
        with rx.session() as session:
            i = session.exec(select(Issuer).where(Issuer.id == issuer["id"])).first()
            if i:
                i.status = "inactive"
                session.add(i)
                session.commit()
                self.load_issuers()
        return rx.window_alert("Issuer deactivated.")

    def activate_issuer(self, issuer: dict):
        with rx.session() as session:
            i = session.exec(select(Issuer).where(Issuer.id == issuer["id"])).first()
            if i:
                i.status = "active"
                session.add(i)
                session.commit()
                self.load_issuers()
        return rx.window_alert("Issuer activated.")
