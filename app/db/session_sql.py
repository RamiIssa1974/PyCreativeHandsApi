from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

params = []
if settings.SQL_TRUST_CERT.lower() == "true":
    params.append("TrustServerCertificate=yes")

conn = (
    f"mssql+pyodbc://{settings.SQLSERVER_USER}:{settings.SQLSERVER_PASSWORD}"
    f"@{settings.SQLSERVER_HOST}/{settings.SQLSERVER_DB}"
    f"?driver={settings.SQL_ODBC_DRIVER.replace(' ', '+')}"
)
if params:
    conn += "&" + "&".join(params)

engine = create_engine(conn, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ping_db() -> bool:
    with engine.connect() as conn_:
        conn_.execute(text("SELECT 1"))
    return True
