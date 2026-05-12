import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class AccountType(str, enum.Enum):
    SAVINGS = "savings"      # Caja de ahorro
    CHECKING = "checking"    # Cuenta corriente
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    VIRTUAL = "virtual"      # Para "reservas" o "sobres"
    DEBT = "debt"            # Lo que le debés a otros o te deben
    INVESTMENTS = "investments"

class Account(Base):
    """Cuentas bancarias, tarjetas, efectivo o sobres virtuales."""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)   
    entity = Column(String, nullable=False) 
    type = Column(Enum(AccountType), nullable=False)
    currency = Column(String(5), default="ARS", nullable=False)
    
    # NUEVO: Define si la cuenta es de liquidez diaria o de ahorro/inversión
    is_day_to_day = Column(Boolean, default=True, nullable=False) # Ej: "ARS", "USD", "USDT"

class Transaction(Base):
    """El contenedor de un evento financiero."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    entries = relationship("Entry", back_populates="transaction", cascade="all, delete-orphan")

class Person(Base):
    """Amigos o entidades para dividir gastos."""
    __tablename__ = "people"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Entry(Base):
    """Cada línea de movimiento de dinero dentro de una transacción."""
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # amount: El valor en la divisa original de la cuenta (ej. 100 USD o 1200000 ARS)
    amount = Column(Numeric(12, 2), nullable=False)
    
    # base_amount: Su valor de conversión unificado a la moneda base (ARS) para cuadrar a cero
    base_amount = Column(Numeric(12, 2), nullable=False)
    
    transaction = relationship("Transaction", back_populates="entries")

class UserSettings(Base):
    """Configuraciones globales y automatizaciones del usuario."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    payday_day = Column(Integer, nullable=True)
    last_confirmed_payday = Column(DateTime, nullable=True) 
    default_income_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)