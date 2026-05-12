from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.DataModels import AccountType

# --- ENTIDADES BASE ---

class AccountCreate(BaseModel):
    name: str
    entity: str 
    type: AccountType
    currency: str = "ARS"
    is_day_to_day: bool = True  # Por defecto va al flujo diario

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
    base_amount: Optional[Decimal] = None
    account_id: Optional[int] = None
    person_id: Optional[int] = None
    category_id: Optional[int] = None

    @field_validator("amount")
    def validate_precision(cls, v: Decimal):
        return round(v, 2)

    @model_validator(mode="after")
    def set_default_base_amount(self):
        # Si no se pasa un base_amount explícito, asumimos que es 1:1 con la moneda base
        if self.base_amount is None:
            self.base_amount = self.amount
        else:
            self.base_amount = round(self.base_amount, 2)
        return self

class TransactionCreate(BaseModel):
    description: str
    date: Optional[datetime] = None
    entries: List[EntryBase]

    @field_validator("entries")
    def check_balance(cls, entries: List[EntryBase]):
        if len(entries) < 2:
            raise ValueError("Una transacción debe tener al menos dos movimientos (partida doble).")
        
        # El balance a cero ahora se exige estrictamente sobre el valor unificado (base_amount)
        total = sum((entry.base_amount for entry in entries), Decimal("0.00"))
        if total != Decimal("0.00"):
            raise ValueError(f"Transacción desbalanceada en moneda base. La suma da {total}, debe ser 0.00.")
        
        return entries

# --- ANALYTICS --- 

class AccountBalance(BaseModel):
    account_id: int
    account_name: str
    entity: str
    balance: Decimal        # Saldo en divisa original (ej. 100 USD)
    base_balance: Decimal   # Equivalencia unificada en ARS (ej. 120000 ARS)
    currency: str
    is_day_to_day: bool

class TotalBalance(BaseModel):
    day_to_day_available: Decimal # Liquidez real para gastar hoy en pesos
    total_assets: Decimal         # Total de activos unificados en pesos
    total_liabilities: Decimal    # Total de pasivos unificados en pesos
    net_worth: Decimal