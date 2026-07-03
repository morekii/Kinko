from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.DataModels import Transaction
from app.schemas.finance import (
    DebtCreate,
    DebtPaymentCreate,
    ExpenseCreate,
    IncomeCreate,
    TransactionCreate,
    TransferCreate,
)
from app.core.transactions_service import (
    MissingRateError,
    create_debt,
    create_debt_payment,
    create_expense,
    create_income,
    create_transfer,
    persist_transaction,
    replace_transaction_entries,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _run_intent(fn, db: Session, payload) -> Dict[str, Any]:
    try:
        tx = fn(db, payload)
    except (MissingRateError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "transaction_id": tx.id}


@router.post("/", status_code=201)
def create_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    db_tx = persist_transaction(db, tx_in)
    return {"status": "success", "transaction_id": db_tx.id}


@router.post("/expense", status_code=201)
def create_expense_transaction(payload: ExpenseCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return _run_intent(create_expense, db, payload)


@router.post("/income", status_code=201)
def create_income_transaction(payload: IncomeCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return _run_intent(create_income, db, payload)


@router.post("/transfer", status_code=201)
def create_transfer_transaction(payload: TransferCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return _run_intent(create_transfer, db, payload)


@router.post("/debt", status_code=201)
def create_debt_transaction(payload: DebtCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return _run_intent(create_debt, db, payload)


@router.post("/debt-payment", status_code=201)
def create_debt_payment_transaction(payload: DebtPaymentCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    return _run_intent(create_debt_payment, db, payload)

@router.get("/")
def list_transactions(skip: int = 0, limit: int = 500, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    transactions = (
        db.query(Transaction)
        .order_by(Transaction.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    result = []
    for tx in transactions:
        entries = [
            {
                "id": e.id,
                "account_id": e.account_id,
                "person_id": e.person_id,
                "category_id": e.category_id,
                "amount": e.amount,
                "base_amount": e.base_amount
            }
            for e in tx.entries
        ]
        
        result.append({
            "id": tx.id,
            "description": tx.description,
            "date": tx.date,
            "entries": entries
        })
        
    return result

# --- NUEVOS ENDPOINTS INDIVIDUALES ---

@router.get("/{transaction_id}")
def get_transaction(transaction_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Obtiene el detalle completo de una sola transacción mediante su ID."""
    db_tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    entries = [
        {
            "id": e.id,
            "account_id": e.account_id,
            "person_id": e.person_id,
            "category_id": e.category_id,
            "amount": e.amount,
            "base_amount": e.base_amount
        }
        for e in db_tx.entries
    ]
    
    return {
        "id": db_tx.id,
        "description": db_tx.description,
        "date": db_tx.date,
        "entries": entries
    }

@router.patch("/{transaction_id}")
def update_transaction(transaction_id: int, tx_in: TransactionCreate, db: Session = Depends(get_db)):
    """Actualiza la cabecera y reescribe los asientos contables manteniendo el balance a cero."""
    db_tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")

    replace_transaction_entries(db, db_tx, tx_in)
    return {"status": "updated", "transaction_id": db_tx.id}

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Elimina permanentemente una transacción y sus líneas en cascada."""
    db_tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    db.delete(db_tx)
    db.commit()
    return None