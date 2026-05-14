from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.DataModels import AccountType

# --- CUENTAS ---

class AccountCreate(BaseModel):
    name: str
    entity: str 
    type: AccountType
    currency: str = "ARS"
    is_day_to_day: bool = True
    is_active: bool = True

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    entity: Optional[str] = None
    type: Optional[AccountType] = None
    currency: Optional[str] = None
    is_day_to_day: Optional[bool] = None
    is_active: Optional[bool] = None

class AccountResponse(AccountCreate):
    id: int
    class Config:
        from_attributes = True

# --- CATEGORÍAS ---

class CategoryCreate(BaseModel):
    name: str
    is_active: bool = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryCreate):
    id: int
    class Config:
        from_attributes = True

# --- PERSONAS / ENTIDADES EXTERNAS ---

class PersonCreate(BaseModel):
    name: str
    is_debt_tracker: bool = False
    is_active: bool = True

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    is_debt_tracker: Optional[bool] = None
    is_active: Optional[bool] = None

class PersonResponse(PersonCreate):
    id: int
    balance: Decimal = Decimal("0.00")
    class Config:
        from_attributes = True
# --- COTIZACIONES MANUALES ---

class ExchangeRateUpdate(BaseModel):
    rates: dict[str, Decimal]

class ExchangeRateResponse(BaseModel):
    currency: str
    rate_to_base: Decimal
    updated_at: datetime
    class Config:
        from_attributes = True

# --- SUSCRIPCIONES / PROGRAMADOS ---

class SubscriptionCreate(BaseModel):
    description: str
    amount: Decimal
    currency: str = "ARS"
    charge_day: int
    suggested_account_id: Optional[int] = None
    category_id: Optional[int] = None
    is_active: bool = True

class SubscriptionResponse(SubscriptionCreate):
    id: int
    class Config:
        from_attributes = True

# --- TRANSACCIONES Y ASIENTOS ---

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
        
        total = sum((entry.base_amount for entry in entries), Decimal("0.00"))
        if total != Decimal("0.00"):
            raise ValueError(f"Transacción desbalanceada en moneda base. La suma da {total}, debe ser 0.00.")
        
        return entries

# --- ANALÍTICAS Y BALANCES --- 

class AccountBalance(BaseModel):
    account_id: int
    account_name: str
    entity: str
    balance: Decimal
    base_balance: Decimal
    currency: str
    is_day_to_day: bool
    is_active: bool

class TotalBalance(BaseModel):
    day_to_day_available: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal