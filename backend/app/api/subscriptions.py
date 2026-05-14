from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.DataModels import Subscription
from app.schemas.finance import SubscriptionCreate, SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["Suscripciones Recurrentes"])

@router.post("/", response_model=SubscriptionResponse, status_code=201)
def create_subscription(sub_in: SubscriptionCreate, db: Session = Depends(get_db)):
    db_sub = Subscription(**sub_in.model_dump())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.get("/", response_model=List[SubscriptionResponse])
def list_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).filter(Subscription.is_active == True).all()

@router.delete("/{subscription_id}", status_code=204)
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    db_sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    db_sub.is_active = False
    db.commit()
    return None