from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.rates_service import RatesFetchError, refresh_rates
from app.models.DataModels import ExchangeRate
from app.schemas.finance import ExchangeRateUpdate, ExchangeRateResponse
from decimal import Decimal

router = APIRouter(prefix="/settings/rates", tags=["Cotizaciones"])

@router.post("/refresh", response_model=List[ExchangeRateResponse])
def refresh_exchange_rates(db: Session = Depends(get_db)):
    """Actualiza Dólar Oficial, Tarjeta, Cripto (dolarapi.com) y BTC en ARS (Coinbase) automáticamente."""
    try:
        return refresh_rates(db)
    except RatesFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@router.patch("/", response_model=List[ExchangeRateResponse])
def upsert_exchange_rates(rates_in: ExchangeRateUpdate, db: Session = Depends(get_db)):
    """Actualiza o inserta cotizaciones manuales para el cruce de divisas."""
    updated_records = []
    for curr, rate in rates_in.rates.items():
        db_rate = db.query(ExchangeRate).filter(ExchangeRate.currency == curr.upper()).first()
        if db_rate:
            db_rate.rate_to_base = rate
        else:
            db_rate = ExchangeRate(currency=curr.upper(), rate_to_base=rate)
            db.add(db_rate)
        updated_records.append(db_rate)
        
    db.commit()
    for r in updated_records:
        db.refresh(r)
    return updated_records

@router.get("/", response_model=List[ExchangeRateResponse])
def list_rates(db: Session = Depends(get_db)):
    return db.query(ExchangeRate).all()