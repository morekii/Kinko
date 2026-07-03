from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.DataModels import Account, AccountType, Entry, ExchangeRate, Transaction
from app.schemas.finance import (
    DebtCreate,
    DebtPaymentCreate,
    EntryBase,
    ExpenseCreate,
    IncomeCreate,
    TransactionCreate,
    TransferCreate,
)


class MissingRateError(Exception):
    def __init__(self, currency: str):
        self.currency = currency
        super().__init__(
            f"No hay cotización configurada para '{currency}'. "
            "Cargala en Configuración → Cotizaciones Manuales."
        )


def resolve_rate(db: Session, currency: str) -> Decimal:
    currency = currency.upper()
    if currency == "ARS":
        return Decimal("1.0")
    rate = db.query(ExchangeRate).filter(ExchangeRate.currency == currency).first()
    if not rate:
        raise MissingRateError(currency)
    return rate.rate_to_base


def resolve_main_account(db: Session) -> Optional[Account]:
    return db.query(Account).filter(Account.is_main == True).first()  # noqa: E712


def _write_entries(db: Session, tx: Transaction, entries: list[EntryBase]) -> None:
    for entry_in in entries:
        db.add(
            Entry(
                transaction_id=tx.id,
                account_id=entry_in.account_id,
                person_id=entry_in.person_id,
                category_id=entry_in.category_id,
                amount=entry_in.amount,
                base_amount=entry_in.base_amount,
            )
        )


def persist_transaction(db: Session, tx_in: TransactionCreate) -> Transaction:
    tx = Transaction(description=tx_in.description, date=tx_in.date)
    db.add(tx)
    db.flush()
    _write_entries(db, tx, tx_in.entries)
    db.commit()
    db.refresh(tx)
    return tx


def replace_transaction_entries(db: Session, tx: Transaction, tx_in: TransactionCreate) -> Transaction:
    tx.description = tx_in.description
    if tx_in.date:
        tx.date = tx_in.date
    for entry in tx.entries:
        db.delete(entry)
    db.flush()
    _write_entries(db, tx, tx_in.entries)
    db.commit()
    return tx


def create_expense(db: Session, payload: ExpenseCreate) -> Transaction:
    rate = resolve_rate(db, payload.currency)
    base_amount = round(payload.amount * rate, 2)

    entries = [
        EntryBase(account_id=payload.account_id, amount=-payload.amount, base_amount=-base_amount),
        EntryBase(
            category_id=payload.category_id,
            person_id=payload.person_id,
            amount=payload.amount,
            base_amount=base_amount,
        ),
    ]

    if payload.reserve_funds:
        account = db.query(Account).filter(Account.id == payload.account_id).first()
        if not account or account.type != AccountType.CREDIT_CARD or not account.reserve_account_id:
            raise ValueError("La cuenta seleccionada no es una tarjeta con cuenta de reserva configurada.")

        source_id = payload.reserve_source_account_id
        if not source_id:
            main_account = resolve_main_account(db)
            source_id = main_account.id if main_account else None
        if not source_id:
            raise ValueError("Configurá una Cuenta Principal o especificá una cuenta de origen para la reserva.")

        entries.append(EntryBase(account_id=source_id, amount=-payload.amount, base_amount=-base_amount))
        entries.append(
            EntryBase(account_id=account.reserve_account_id, amount=payload.amount, base_amount=base_amount)
        )

    tx_in = TransactionCreate(description=payload.description or "Gasto", date=payload.date, entries=entries)
    return persist_transaction(db, tx_in)


def create_income(db: Session, payload: IncomeCreate) -> Transaction:
    rate = resolve_rate(db, payload.currency)
    base_amount = round(payload.amount * rate, 2)

    entries = [
        EntryBase(account_id=payload.account_id, amount=payload.amount, base_amount=base_amount),
        EntryBase(
            category_id=payload.category_id,
            person_id=payload.person_id,
            amount=-payload.amount,
            base_amount=-base_amount,
        ),
    ]
    tx_in = TransactionCreate(description=payload.description or "Ingreso", date=payload.date, entries=entries)
    return persist_transaction(db, tx_in)


def create_transfer(db: Session, payload: TransferCreate) -> Transaction:
    source_rate = resolve_rate(db, payload.currency)
    base_amount = round(payload.amount * source_rate, 2)
    fee_base = round(payload.fee_amount * source_rate, 2) if payload.fee_amount else Decimal("0.00")

    destination = db.query(Account).filter(Account.id == payload.destination_account_id).first()
    if not destination:
        raise ValueError("Cuenta destino inválida.")

    if payload.destination_amount is not None:
        destination_amount = payload.destination_amount
    elif destination.currency == payload.currency:
        destination_amount = payload.amount
    else:
        dest_rate = resolve_rate(db, destination.currency)
        destination_amount = round(base_amount / dest_rate, 6)

    entries = [
        EntryBase(
            account_id=payload.source_account_id,
            amount=-(payload.amount + payload.fee_amount),
            base_amount=-(base_amount + fee_base),
        ),
        EntryBase(account_id=payload.destination_account_id, amount=destination_amount, base_amount=base_amount),
    ]
    if payload.fee_amount:
        entries.append(
            EntryBase(category_id=payload.fee_category_id, amount=payload.fee_amount, base_amount=fee_base)
        )

    tx_in = TransactionCreate(description=payload.description or "Transferencia", date=payload.date, entries=entries)
    return persist_transaction(db, tx_in)


def create_debt(db: Session, payload: DebtCreate) -> Transaction:
    rate = resolve_rate(db, payload.currency)
    base_amount = round(payload.amount * rate, 2)

    entries = [
        EntryBase(category_id=payload.category_id, amount=payload.amount, base_amount=base_amount),
        EntryBase(person_id=payload.person_id, amount=-payload.amount, base_amount=-base_amount),
    ]
    tx_in = TransactionCreate(description=payload.description or "Gasto a Pagar", date=payload.date, entries=entries)
    return persist_transaction(db, tx_in)


def create_debt_payment(db: Session, payload: DebtPaymentCreate) -> Transaction:
    rate = resolve_rate(db, payload.currency)
    base_amount = round(payload.amount * rate, 2)

    entries = [
        EntryBase(account_id=payload.account_id, amount=-payload.amount, base_amount=-base_amount),
        EntryBase(person_id=payload.person_id, amount=payload.amount, base_amount=base_amount),
    ]
    tx_in = TransactionCreate(description=payload.description or "Pago de Deuda", date=payload.date, entries=entries)
    return persist_transaction(db, tx_in)
