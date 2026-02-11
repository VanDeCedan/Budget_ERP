from sqlmodel import select, Session
from ..models.ptab import Ptab
from ..models.sub_request import SubRequest
from ..models.expenses import Expenses
from ..models.reconciliation import Reconciliation
from ..models.regularisation import Regularisation
from ..models.balance import Balance

def recalculate_balances(session: Session):
    """
    Recalculates the balance for all active PTAB lines.
    Logic:
    Balance = PTAB Amount - Sum(Effective Expenses)
    
    Effective Expense:
    - If Expense is used by an ACTIVE Regularisation -> use Regularisation.amount
    - Else if Parent SubRequest is ACTIVE -> use Expense.amount
    - Else -> 0
    """
    # 1. Get all active PTABs
    ptabs = session.exec(select(Ptab).where(Ptab.status == "active")).all()
    if not ptabs:
        # Clear balance table if no active PTABs
        session.exec(select(Balance)).all() # Just to be sure we can clear
        for b in session.exec(select(Balance)).all():
            session.delete(b)
        return

    # 2. Get helpers for calculations
    # Active Reconciliations
    active_recons = session.exec(select(Reconciliation).where(Reconciliation.status == "active")).all()
    active_recon_ids = {r.id for r in active_recons}
    
    # Regularisations for active recons
    # Map: expenses_id -> amount
    reg_lookup = {}
    if active_recon_ids:
        # This is a bit brute force, but works for the current scale
        regs = session.exec(select(Regularisation)).all()
        for reg in regs:
            if reg.reconci_id in active_recon_ids:
                reg_lookup[reg.expenses_id] = reg.amount
                
    # Active SubRequests
    active_srs = session.exec(select(SubRequest).where(SubRequest.status == "active")).all()
    active_sr_ids = {sr.id for sr in active_srs}

    # 3. Calculate and Sync
    # We clear existing balances to ensure we only have records for current active PTABs
    for b in session.exec(select(Balance)).all():
        session.delete(b)
    session.flush()

    for ptab in ptabs:
        total_spent = 0
        # Find all expenses for this ptab
        expenses = session.exec(select(Expenses).where(Expenses.ptab_id == ptab.id)).all()
        
        for exp in expenses:
            # Reconciliated?
            if exp.id in reg_lookup:
                total_spent += reg_lookup[exp.id]
            # Active request but not reconciliated?
            elif exp.sub_request_id in active_sr_ids:
                total_spent += exp.amount
            # Else (canceled/deleted) -> 0 spent
            
        new_balance = Balance(
            ptab_id=ptab.id,
            amount=ptab.amount - total_spent
        )
        session.add(new_balance)
