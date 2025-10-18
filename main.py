from fastapi import FastAPI
from app.core.config import get_settings
from app.db.session_sql import ping_db
from app.routers import products

settings = get_settings()
show_docs = settings.ENV.lower() != "prod"  
app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/docs" if show_docs else None,
    redoc_url="/redoc" if show_docs else None,
    openapi_url="/openapi.json" if show_docs else None,
)


app.include_router(products.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.ENV, "provider": settings.DATA_PROVIDER}

@app.get("/health/db")
def health_db():
    ping_db()
    return {"db": "ok"}
