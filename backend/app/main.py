from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import transactions, entities, analytics, settings, subscriptions, notifications
from app.core.database import Base, engine
from app.core.scheduler import start_scheduler # <-- IMPORTAMOS EL MOTOR

# Creamos las tablas si no existen (SQLite)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- LO QUE PASA AL ARRANCAR ---
    print("Iniciando motor de suscripciones automáticas...")
    start_scheduler()
    yield
    # --- LO QUE PASA AL APAGAR ---
    print("Apagando servidores...")

# Iniciamos FastAPI con el lifespan
app = FastAPI(title="Kinko API", lifespan=lifespan)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kinko-app.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos las rutas
app.include_router(transactions.router)
app.include_router(entities.router)
app.include_router(analytics.router)
app.include_router(settings.router)
app.include_router(subscriptions.router)
app.include_router(notifications.router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Kinko API"}