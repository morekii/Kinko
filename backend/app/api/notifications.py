from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import BaseModel

from app.core.database import get_db
from app.models.DataModels import Notification, Account, Transaction, Entry

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    action_type: str
    amount: Decimal
    is_resolved: bool

@router.get("/", response_model=list[NotificationResponse])
def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.is_resolved == False).all()

@router.post("/{notif_id}/resolve")
def resolve_notification(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif or notif.is_resolved:
        return {"status": "already resolved"}

    if notif.action_type == "reserve_funds":
        # 1. Buscamos tu cuenta principal
        main_acc = db.query(Account).filter(Account.is_main == True).first()
        if not main_acc:
            raise HTTPException(400, "Configurá una Cuenta Principal primero.")

        # 2. Buscamos el sobre de reserva de esa tarjeta
        credit_acc = db.query(Account).filter(Account.id == notif.credit_account_id).first()
        if not credit_acc or not credit_acc.reserve_account_id:
            raise HTTPException(400, "La tarjeta perdió su cuenta de reserva.")

        # 3. Transacción automática de reserva
        tx = Transaction(description=f"Reserva auto: {notif.title}", date=datetime.now(timezone.utc))
        db.add(tx)
        db.flush()

        db.add(Entry(transaction_id=tx.id, account_id=main_acc.id, amount=-notif.amount, base_amount=-notif.base_amount))
        db.add(Entry(transaction_id=tx.id, account_id=credit_acc.reserve_account_id, amount=notif.amount, base_amount=notif.base_amount))

    notif.is_resolved = True
    db.commit()
    return {"status": "resolved"}

@router.post("/{notif_id}/dismiss")
def dismiss_notification(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if notif:
        notif.is_resolved = True
        db.commit()
    return {"status": "dismissed"}