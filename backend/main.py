from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.routes import user_routes, auth
from app.core.error_handlers import register_error_handlers
from app.core.database import engine, Base

# Importa modelos para registrar metadata antes de create_all
from app.models.user import User  # noqa: F401

app = FastAPI(title="ACI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
api_router = APIRouter(prefix="/api")
api_router.include_router(user_routes.router)
api_router.include_router(auth.router)  

app.include_router(api_router)

register_error_handlers(app)

# ✅ Metadata de User
Base.metadata.create_all(bind=engine)
