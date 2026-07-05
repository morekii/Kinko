import time
from decimal import Decimal

import httpx
from sqlalchemy.orm import Session

from app.models.DataModels import ExchangeRate

DOLARAPI_BASE = "https://dolarapi.com/v1/dolares"
COINBASE_BTC_USD = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1.5


class RatesFetchError(Exception):
    pass


def _with_retries(fn):
    last_exc = None
    for attempt in range(RETRY_ATTEMPTS):
        try:
            return fn()
        except httpx.HTTPError as exc:
            last_exc = exc
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_BACKOFF_SECONDS * (2 ** attempt))
    raise last_exc


def _fetch_dolar_venta(tipo: str) -> Decimal:
    def call():
        resp = httpx.get(f"{DOLARAPI_BASE}/{tipo}", timeout=10)
        resp.raise_for_status()
        return Decimal(str(resp.json()["venta"]))

    return _with_retries(call)


def _fetch_btc_usd() -> Decimal:
    def call():
        resp = httpx.get(COINBASE_BTC_USD, timeout=10)
        resp.raise_for_status()
        return Decimal(resp.json()["data"]["amount"])

    return _with_retries(call)


def fetch_external_rates() -> dict[str, Decimal]:
    """Trae Oficial, Tarjeta y Cripto de dolarapi.com, y BTC-USD de Coinbase.
    BTC se guarda ya convertido a ARS usando el dólar cripto, que es la
    referencia real que se usa para operar cripto en Argentina."""
    try:
        oficial = _fetch_dolar_venta("oficial")
        tarjeta = _fetch_dolar_venta("tarjeta")
        cripto = _fetch_dolar_venta("cripto")
        btc_usd = _fetch_btc_usd()
    except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
        raise RatesFetchError(f"No se pudieron obtener las cotizaciones externas: {exc}") from exc

    return {
        "USD_OFICIAL": oficial,
        "USD_TARJETA": tarjeta,
        "USD_CRIPTO": cripto,
        "BTC": (btc_usd * cripto).quantize(Decimal("0.01")),
    }


def refresh_rates(db: Session) -> list[ExchangeRate]:
    values = fetch_external_rates()
    updated = []
    for currency, rate in values.items():
        db_rate = db.query(ExchangeRate).filter(ExchangeRate.currency == currency).first()
        if db_rate:
            db_rate.rate_to_base = rate
        else:
            db_rate = ExchangeRate(currency=currency, rate_to_base=rate)
            db.add(db_rate)
        updated.append(db_rate)

    db.commit()
    for r in updated:
        db.refresh(r)
    return updated
