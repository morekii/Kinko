from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.DataModels import AccountType

# --- ENTIDADES BASE ---

class AccountCreate(BaseModel):
    name: str
    entity: str 
    type: AccountType

class AccountResponse(AccountCreate):
    id: int
    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(CategoryCreate):
    id: int
    class Config:
        from_attributes = True

class PersonCreate(BaseModel):
    name: str

class PersonResponse(PersonCreate):
    id: int
    class Config:
        from_attributes = True

# --- TRANSACCIONES ---

class EntryBase(BaseModel):
    amount: Decimal
    account_id: Optional[int] = None
    person_id: Optional[int] = None
    category_id: Optional[int] = None

    @field_validator("amount")
    def validate_precision(cls, v: Decimal):
        return round(v, 2)

class TransactionCreate(BaseModel):
    description: str
    date: Optional[datetime] = None
    entries: List[EntryBase]

    @field_validator("entries")
    def check_balance(cls, entries: List[EntryBase]):
        if len(entries) < 2:
            raise ValueError("Una transacción debe tener al menos dos movimientos (partida doble).")
        
        total = sum((entry.amount for entry in entries), Decimal("0.00"))
        if total != Decimal("0.00"):
            raise ValueError(f"Transacción desbalanceada. La suma de los movimientos da {total}, debe ser 0.00.")
        
        return entries

# --- ANALYTICS --- 

class AccountBalance(BaseModel):
    account_id: int
    account_name: str
    entity: str
    balance: Decimal
    currency: str = "ARS" # Por ahora hardcodeamos ARS, luego podemos sumarlo al modelo

class TotalBalance(BaseModel):
    total_assets: Decimal    # Lo que tenés (Cuentas, Efectivo)
    total_liabilities: Decimal # Lo que debés (Tarjetas, Deudas con personas)
    net_worth: Decimal       # La diferencia