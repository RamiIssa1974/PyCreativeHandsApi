from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session_sql import ping_db
from app.routers import products

settings = get_settings()
show_docs = settings.ENV.lower() != "prod"  
ALLOWED_ORIGINS = [
    "https://your-react-site.com",       # prod site
    "http://localhost:3000",             # CRA dev
    "https://localhost:3000",
    "http://localhost:5173",             # Vite dev
    "http://creativehandsco.com",
    "https://creativehandsco.com",
    "http://py.creativehandsco.com",
    "https://py.creativehandsco.com",
]

app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/docs" if show_docs else None,
    redoc_url="/redoc" if show_docs else None,
    openapi_url="/openapi.json" if show_docs else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.ENV, "provider": settings.DATA_PROVIDER}

@app.get("/health/db")
def health_db():
    ping_db()
    return {"db": "ok"}
