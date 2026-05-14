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
    
    db_tx.description = tx_in.description
    if tx_in.date:
        db_tx.date = tx_in.date

    # Eliminamos las líneas previas para evitar duplicaciones o desbalances
    for entry in db_tx.entries:
        db.delete(entry)
    db.flush()

    # Insertamos las nuevas líneas modificadas
    for entry_in in tx_in.entries:
        db_entry = Entry(
            transaction_id=db_tx.id,
            account_id=entry_in.account_id,
            person_id=entry_in.person_id,
            category_id=entry_in.category_id,
            amount=entry_in.amount,
            base_amount=entry_in.base_amount
        )
        db.add(db_entry)

    db.commit()
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