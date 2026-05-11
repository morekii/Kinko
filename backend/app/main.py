from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import DataModels
from app.api import transactions, entities, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kinko API",
    description="Motor backend para finanzas personales con partida doble",
    version="1.0.0"
)

# Conectamos los routers
app.include_router(entities.router)
app.include_router(transactions.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"status": "Kinko API online", "db_mode": "SQLite temporal"}