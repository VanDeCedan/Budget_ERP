import reflex as rx
from typing import List, Dict, Any
import pandas as pd
import io
from sqlmodel import select
from ..models.ptab import Ptab
from ..models.balance import Balance
from .base import BaseState

class SoldeState(BaseState):
    solde_data: List[Dict[str, Any]] = []
    
    # Filter fields
    filter_year: str = "all"
    filter_activity_code: str = ""
    filter_project: str = "all"
    applied_year: str = "all"
    applied_activity_code: str = ""
    applied_project: str = "all"

    def load_solde(self):
        with rx.session() as session:
            # Load active PTABs
            ptabs = session.exec(select(Ptab).where(Ptab.status == "active")).all()
            
            # Load all Balances
            balances = session.exec(select(Balance)).all()
            balance_map = {b.ptab_id: b.amount for b in balances}
            
            self.solde_data = []
            for p in ptabs:
                self.solde_data.append({
                    "year": p.year,
                    "project": p.projet,
                    "project_code": p.projet_code,
                    "item_code": p.item_code,
                    "activity_code": p.activity_code,
                    "baseline_amount": p.amount,
                    "balance": balance_map.get(p.id, p.amount),
                    "is_negative": balance_map.get(p.id, p.amount) < 0
                })

    @rx.var
    def display_solde(self) -> List[Dict[str, Any]]:
        filtered = []
        for d in self.solde_data:
            # Year Filter
            if self.applied_year != "all" and str(d["year"]) != self.applied_year:
                continue
            # Project Filter
            if self.applied_project != "all" and d["project"] != self.applied_project:
                continue
            # Activity Code Filter
            if self.applied_activity_code and self.applied_activity_code not in str(d["activity_code"]):
                continue
            filtered.append(d)
        return filtered

    def set_filter_year(self, value: str):
        self.filter_year = value

    def set_filter_activity_code(self, value: str):
        self.filter_activity_code = value

    def set_filter_project(self, value: str):
        self.filter_project = value

    def apply_table_filters(self):
        self.applied_year = self.filter_year
        self.applied_activity_code = self.filter_activity_code
        self.applied_project = self.filter_project

    def reset_table_filters(self):
        self.filter_year = "all"
        self.filter_activity_code = ""
        self.filter_project = "all"
        self.applied_year = "all"
        self.applied_activity_code = ""
        self.applied_project = "all"

    def download_solde_excel(self):
        """Generates an Excel file from the filtered solde data."""
        if not self.display_solde:
            return rx.window_alert("Aucune donnée à télécharger.")
            
        df = pd.DataFrame(self.display_solde)
        # Rename columns for clarity in Excel
        column_mapping = {
            "year": "Année",
            "project": "Projet",
            "project_code": "Code Projet",
            "item_code": "Code Item",
            "activity_code": "Code Activité",
            "baseline_amount": "Budget Initial",
            "balance": "Solde Actuel"
        }
        # Drop columns not needed in Excel (like is_negative)
        df = df[[col for col in column_mapping.keys() if col in df.columns]]
        df = df.rename(columns=column_mapping)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output) as writer:
            df.to_excel(writer, index=False, sheet_name='Solde')
        
        return rx.download(
            data=output.getvalue(),
            filename=f"solde_budgetaire_{self.applied_year}_{self.applied_project}.xlsx"
        )
