from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.models.DataModels import Account, Entry
from app.schemas.finance import AccountBalance, TotalBalance
from decimal import Decimal

router = APIRouter(prefix="/analytics", tags=["Analytics & Balances"])

@router.get("/balances", response_model=List[AccountBalance])
def get_account_balances(db: Session = Depends(get_db)):
    """Calcula el saldo actual nativo y en moneda base para cada cuenta."""
    results = (
        db.query(
            Account.id,
            Account.name,
            Account.entity,
            Account.currency,
            Account.is_day_to_day,
            func.sum(Entry.amount).label("total_balance"),
            func.sum(Entry.base_amount).label("total_base_balance")
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
            balance=r.total_balance or Decimal("0.00"),
            base_balance=r.total_base_balance or Decimal("0.00"),
            currency=r.currency,
            is_day_to_day=r.is_day_to_day
        ) for r in results
    ]

@router.get("/net-worth", response_model=TotalBalance)
def get_net_worth(db: Session = Depends(get_db)):
    """Calcula el patrimonio neto total y la liquidez diaria usando equivalencias unificadas."""
    balances = get_account_balances(db)
    
    # 1. Dinero disponible Día a Día (solo cuentas marcadas para uso diario con saldo positivo)
    day_to_day = sum((b.base_balance for b in balances if b.is_day_to_day and b.base_balance > 0), Decimal("0.00"))
    
    # 2. Activos y Pasivos Globales (utilizando siempre la columna unificada base_balance)
    assets = sum((b.base_balance for b in balances if b.base_balance > 0), Decimal("0.00"))
    liabilities = sum((b.base_balance for b in balances if b.base_balance < 0), Decimal("0.00"))
    
    return TotalBalance(
        day_to_day_available=day_to_day,
        total_assets=assets,
        total_liabilities=abs(liabilities),
        net_worth=assets + liabilities
    )