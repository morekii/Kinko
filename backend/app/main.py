from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import transactions, entities, analytics, settings, subscriptions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kinko API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entities.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(settings.router)
app.include_router(subscriptions.router)

@app.get("/")
def read_root():
    return {"status": "Kinko API online"}