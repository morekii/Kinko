import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum
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

class Transaction(Base):
    """El contenedor de un evento financiero."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Una transacción tiene muchos movimientos (mínimo 2 para balancear)
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
    
    # ¿A dónde va/viene la plata? Puede ser una cuenta, una persona o una categoría de gasto
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # El monto: Negativo es salida, Positivo es entrada/gasto/deuda
    # En este sistema, la SUMA de todos los amounts de una Transaction DEBE ser 0
    amount = Column(Numeric(12, 2), nullable=False)
    
    transaction = relationship("Transaction", back_populates="entries")

class UserSettings(Base):
    """Configuraciones globales y automatizaciones del usuario."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    payday_day = Column(Integer, nullable=True)  # Día del mes (ej. 1 al 5)
    
    # Guarda el último mes/año en que se confirmó el cobro para no volver a preguntar
    last_confirmed_payday = Column(DateTime, nullable=True) 
    
    # Cuenta por defecto a la que suele entrar el sueldo
    default_income_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)