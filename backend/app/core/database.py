import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Por defecto usamos SQLite para desarrollar sin depender de Postgres.
# En Railway (o el rig, cuando esté listo) se define DATABASE_URL, por ejemplo:
# postgresql+psycopg://kinko_user:password@localhost:5432/kinko
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./kinko_dev.db")
IS_SQLITE = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

# connect_args={"check_same_thread": False} es una exigencia exclusiva de SQLite en aplicaciones multihilo como FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)

if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def _enable_wal_mode(dbapi_connection, connection_record):
        # Modo WAL: permite que el scheduler en background y los requests de la API
        # lean/escriban sin bloquearse entre sí. Solo aplica a SQLite.
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Generador para inyectar la sesión de base de datos en los endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()