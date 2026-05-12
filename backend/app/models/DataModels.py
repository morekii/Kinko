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
    currency = Column(String(5), default="ARS", nullable=False) # Permite "ARS", "USD", "USDT", "BTC"
    is_day_to_day = Column(Boolean, default=True, nullable=False)
    
    # Soft Delete para mantener trazabilidad histórica
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Fechas clave para gestión de tarjetas de crédito
    closing_day = Column(Integer, nullable=True)  # Día de cierre del resumen (1-31)
    due_day = Column(Integer, nullable=True)      # Día de vencimiento del pago (1-31)

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
    is_active = Column(Boolean, default=True, nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)

class Entry(Base):
    """Cada línea de movimiento de dinero dentro de una transacción."""
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    amount = Column(Numeric(18, 4), nullable=False)      # Precisión ampliada para soportar fracciones de BTC
    base_amount = Column(Numeric(18, 2), nullable=False) # Equivalencia en moneda base (ARS) para cuadrar a cero
    
    transaction = relationship("Transaction", back_populates="entries")

class ExchangeRate(Base):
    """Almacena tasas de cambio manuales o consultadas para divisas vs la moneda base (ARS)."""
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True)
    currency = Column(String(5), unique=True, nullable=False) # Ej: "USD", "BTC"
    rate_to_base = Column(Numeric(18, 4), nullable=False)     # Cuántos ARS equivale 1 unidad de esta divisa
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Subscription(Base):
    """Plantillas para gastos recurrentes o deudas mensuales programadas."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(5), default="ARS", nullable=False)
    
    # Día configurado de cobro/vencimiento en el mes (1-31)
    charge_day = Column(Integer, nullable=False)
    
    # Opcional: Cuenta sugerida de origen y categoría de gasto por defecto
    suggested_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)

class UserSettings(Base):
    """Configuraciones globales y automatizaciones del usuario."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    payday_day = Column(Integer, nullable=True)
    last_confirmed_payday = Column(DateTime, nullable=True) 
    default_income_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)