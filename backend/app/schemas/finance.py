from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class EntryBase(BaseModel):
    amount: Decimal
    account_id: Optional[int] = None
    person_id: Optional[int] = None
    category_id: Optional[int] = None

    @field_validator("amount")
    def validate_precision(cls, v: Decimal):
        # Aseguramos que no tenga más de 2 decimales
        return round(v, 2)

class TransactionCreate(BaseModel):
    description: str
    date: Optional[datetime] = None
    entries: List[EntryBase]

    @field_validator("entries")
    def check_balance(cls, entries: List[EntryBase]):
        if len(entries) < 2:
            raise ValueError("Una transacción debe tener al menos dos movimientos (partida doble).")
        
        # Validamos estrictamente que la suma de todos los amounts sea exactamente 0.00
        total = sum((entry.amount for entry in entries), Decimal("0.00"))
        if total != Decimal("0.00"):
            raise ValueError(f"Transacción desbalanceada. La suma de los movimientos da {total}, debe ser 0.00.")
        
        return entries