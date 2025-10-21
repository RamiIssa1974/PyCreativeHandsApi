from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session_sql import ping_db
from app.routers import products
from app.routers import orders,auth
from app.routers import purchase as purchase_router
from app.routers import upload as upload_router
from app.routers import video as video_router

load_dotenv()
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
app.include_router(orders.router, prefix="/api")
app.include_router(orders.router)
app.include_router(auth.router, prefix="/api")
app.include_router(auth.router)
app.include_router(purchase_router.router, prefix="/api/purchases", tags=["Purchase"])
app.include_router(purchase_router.router, prefix="/api/Purchases", tags=["Purchase"])
app.include_router(purchase_router.router, prefix="/purchases", tags=["Purchase"])
app.include_router(purchase_router.router, prefix="/Purchases", tags=["Purchase"])
app.include_router(upload_router.router, tags=["Upload"])
app.include_router(video_router.router, prefix="/api/video", tags=["Video"])
app.include_router(video_router.router, prefix="/api/Video", tags=["Video"])
app.include_router(video_router.router, prefix="/video", tags=["Video"])
app.include_router(video_router.router, prefix="/Video", tags=["Video"])






@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.ENV, "provider": settings.DATA_PROVIDER}

@app.get("/health/db")
def health_db():
    ping_db()
    return {"db": "ok"}
