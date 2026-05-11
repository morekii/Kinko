from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.DataModels import Transaction, Entry
from app.schemas.finance import TransactionCreate

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", status_code=201)
def create_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Crea una transacción financiera atómica.
    Pydantic ya garantizó en este punto que la suma de todos los 'entries' da exactamente 0.00.
    """
    # 1. Crear la cabecera de la transacción
    db_tx = Transaction(
        description=tx_in.description,
        date=tx_in.date  # Si enviaron None, el modelo asignará la fecha UTC actual
    )
    db.add(db_tx)
    db.flush()  # Asigna el ID a db_tx dentro de la sesión sin hacer el commit definitivo

    # 2. Insertar cada una de las líneas de movimiento (partida doble)
    for entry_in in tx_in.entries:
        db_entry = Entry(
            transaction_id=db_tx.id,
            account_id=entry_in.account_id,
            person_id=entry_in.person_id,
            category_id=entry_in.category_id,
            amount=entry_in.amount
        )
        db.add(db_entry)

    # 3. Confirmar e impactar la transacción completa en la base de datos
    db.commit()
    db.refresh(db_tx)
    
    return {"status": "success", "transaction_id": db_tx.id}

@router.get("/")
def list_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Lista las transacciones ordenadas de las más recientes a las más antiguas,
    incluyendo el detalle de sus movimientos.
    """
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
                "amount": e.amount
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