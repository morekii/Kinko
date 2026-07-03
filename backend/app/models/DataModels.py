import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class AccountType(str, enum.Enum):
    SAVINGS = "savings"
    CHECKING = "checking"
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    VIRTUAL = "virtual"
    DEBT = "debt"
    INVESTMENTS = "investments"

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)   
    entity = Column(String, nullable=False) 
    type = Column(Enum(AccountType), nullable=False)
    currency = Column(String(5), default="ARS", nullable=False)
    is_day_to_day = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    reserve_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    is_main = Column(Boolean, default=False, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    entries = relationship("Entry", back_populates="transaction", cascade="all, delete-orphan")

class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    # NUEVO: Define si su saldo impacta en el cálculo de Activos/Pasivos Totales
    is_debt_tracker = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)

class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    base_amount = Column(Numeric(12, 2), nullable=False)
    transaction = relationship("Transaction", back_populates="entries")

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id = Column(Integer, primary_key=True)
    currency = Column(String(15), unique=True, nullable=False)
    rate_to_base = Column(Numeric(18, 4), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(5), default="ARS", nullable=False)
    charge_day = Column(Integer, nullable=False)
    suggested_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

class UserSettings(Base):
    __tablename__ = "user_settings"
    id = Column(Integer, primary_key=True)
    payday_day = Column(Integer, nullable=True)
    last_confirmed_payday = Column(DateTime, nullable=True) 
    default_income_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=True)
    base_amount = Column(Numeric(12, 2), nullable=True)
    credit_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))