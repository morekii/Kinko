from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Importar esto
from app.core.database import engine, Base
from app.models import DataModels
from app.api import transactions, entities, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kinko API", version="1.0.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción pondremos la URL de la PWA
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entities.router)
app.include_router(transactions.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"status": "Kinko API online"}