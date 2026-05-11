from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.models.DataModels import Account, Entry, AccountType
from app.schemas.finance import AccountBalance, TotalBalance
from decimal import Decimal

router = APIRouter(prefix="/analytics", tags=["Analytics & Balances"])

@router.get("/balances", response_model=List[AccountBalance])
def get_account_balances(db: Session = Depends(get_db)):
    """Calcula el saldo actual de cada cuenta sumando sus movimientos."""
    # Agrupamos por cuenta y sumamos los montos
    results = (
        db.query(
            Account.id,
            Account.name,
            Account.entity,
            func.sum(Entry.amount).label("total_balance")
        )
        .join(Entry, Account.id == Entry.account_id)
        .group_by(Account.id)
        .all()
    )

    return [
        AccountBalance(
            account_id=r.id,
            account_name=r.name,
            entity=r.entity,
            balance=r.total_balance or Decimal("0.00")
        ) for r in results
    ]

@router.get("/net-worth", response_model=TotalBalance)
def get_net_worth(db: Session = Depends(get_db)):
    """Calcula el patrimonio neto total dividiendo activos y pasivos."""
    balances = get_account_balances(db)
    
    assets = sum((b.balance for b in balances if b.balance > 0), Decimal("0.00"))
    liabilities = sum((b.balance for b in balances if b.balance < 0), Decimal("0.00"))
    
    return TotalBalance(
        total_assets=assets,
        total_liabilities=abs(liabilities),
        net_worth=assets + liabilities
    )