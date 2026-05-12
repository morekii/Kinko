from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.DataModels import Transaction, Entry
from app.schemas.finance import TransactionCreate

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", status_code=201)
def create_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    # 1. Crear la cabecera de la transacción
    db_tx = Transaction(
        description=tx_in.description,
        date=tx_in.date
    )
    db.add(db_tx)
    db.flush()

    # 2. Insertar cada una de las líneas de movimiento con su base_amount
    for entry_in in tx_in.entries:
        db_entry = Entry(
            transaction_id=db_tx.id,
            account_id=entry_in.account_id,
            person_id=entry_in.person_id,
            category_id=entry_in.category_id,
            amount=entry_in.amount,
            base_amount=entry_in.base_amount  # Mapeamos el nuevo campo
        )
        db.add(db_entry)

    # 3. Confirmar la transacción
    db.commit()
    db.refresh(db_tx)
    
    return {"status": "success", "transaction_id": db_tx.id}

@router.get("/")
def list_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
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