from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import calendar

# Importamos la conexión a la BD y los modelos
from app.core.database import SessionLocal
from app.models.DataModels import Account, Notification, Subscription, Transaction, Entry
from app.core.transactions_service import MissingRateError, resolve_rate
from app.core.rates_service import RatesFetchError, refresh_rates


def refresh_daily_rates():
    """Se ejecuta cada madrugada para traer Oficial/Tarjeta/Cripto/BTC de las APIs externas."""
    db: Session = SessionLocal()
    try:
        refresh_rates(db)
        print(f"[{datetime.now(timezone.utc)}] Cotizaciones externas actualizadas.")
    except RatesFetchError as e:
        print(f"No se pudieron actualizar las cotizaciones externas: {e}")
    finally:
        db.close()

def process_daily_subscriptions():
    """Se ejecuta cada medianoche para cobrar suscripciones automáticamente."""
    db: Session = SessionLocal()
    try:
        today = datetime.now(timezone.utc)
        current_day = today.day
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]

        # Si hoy es el último día del mes, cobramos las de hoy Y las de los días que faltan (ej. 29, 30, 31)
        if current_day == last_day_of_month:
            subs = db.query(Subscription).filter(
                Subscription.is_active == True,
                Subscription.charge_day >= current_day
            ).all()
        else:
            # Sino, solo cobramos las que caen exactamente hoy
            subs = db.query(Subscription).filter(
                Subscription.is_active == True,
                Subscription.charge_day == current_day
            ).all()

        if not subs:
            return  # No hay nada que cobrar hoy

        charged_count = 0

        for sub in subs:
            try:
                rate = resolve_rate(db, sub.currency)
            except MissingRateError:
                db.add(Notification(
                    title=f"No se pudo cobrar {sub.description}",
                    message=f"Falta configurar la cotización de {sub.currency} para cobrar esta suscripción automáticamente.",
                    action_type="rate_missing",
                    amount=sub.amount,
                    credit_account_id=sub.suggested_account_id,
                ))
                continue

            # 1. Crear la cabecera de la Transacción
            tx = Transaction(
                description=f"🔄 Auto: {sub.description}",
                date=today
            )
            db.add(tx)
            db.flush()  # Guardamos para obtener el ID

            # 2. Calcular montos
            val = sub.amount
            base_val = val * rate

            # 3. Asiento de SALIDA (De tu cuenta o tarjeta)
            db.add(Entry(
                transaction_id=tx.id,
                account_id=sub.suggested_account_id,
                amount=-val,
                base_amount=-base_val
            ))

            # 4. Asiento de ENTRADA (A la Categoría del gasto)
            db.add(Entry(
                transaction_id=tx.id,
                category_id=sub.category_id,
                amount=val,
                base_amount=base_val
            ))

            acc = db.query(Account).filter(Account.id == sub.suggested_account_id).first()
            if acc and acc.type.value == "credit_card" and acc.reserve_account_id:
                notif = Notification(
                    title=sub.description,
                    message=f"Se cobró {sub.description} en la tarjeta. ¿Querés reservar la plata?",
                    action_type="reserve_funds",
                    amount=val,
                    base_amount=base_val,
                    credit_account_id=acc.id
                )
                db.add(notif)

            charged_count += 1

        db.commit()
        print(f"[{today.strftime('%Y-%m-%d %H:%M:%S')}] Se cobraron {charged_count} de {len(subs)} suscripciones automáticamente.")

    except Exception as e:
        db.rollback()
        print(f"Error en el motor de suscripciones: {e}")
    finally:
        db.close()

# Creamos la instancia del planificador
scheduler = BackgroundScheduler()

def start_scheduler():
    """Inicia el motor en segundo plano."""
    # Cotizaciones primero, para que las suscripciones cobren con datos del día
    scheduler.add_job(
        refresh_daily_rates,
        CronTrigger(hour=0, minute=0, timezone="America/Argentina/Buenos_Aires")
    )
    # Programamos la tarea para que corra todos los días a las 00:01 AM (hora Argentina)
    scheduler.add_job(
        process_daily_subscriptions,
        CronTrigger(hour=0, minute=1, timezone="America/Argentina/Buenos_Aires")
    )
    scheduler.start()
