from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routes import (
    asignacion_routes,
    calificacion_routes,
    catalogo_routes,
    chat_routes,
    comision_routes,
    disponibilidad_routes,
    auth,
    averia_routes,
    factura_routes,
    gestion_routes,
    metrica_routes,
    notificacion_routes,
    orden_routes,
    operacion_routes,
    pago_routes,
    presupuesto_routes,
    push_routes,
    seleccion_taller_routes,
    user_routes,
    vehiculo_routes,
)
from app.core.error_handlers import register_error_handlers
from app.core.database import engine, Base

# Importa modelos para registrar metadata antes de create_all
import app.models  # noqa: F401

app = FastAPI(title="ACI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos de media
if os.path.exists("media"):
    app.mount("/media", StaticFiles(directory="media"), name="media")

# Routers
api_router = APIRouter(prefix="/api")
api_router.include_router(user_routes.router)
api_router.include_router(auth.router)
api_router.include_router(gestion_routes.router)
api_router.include_router(vehiculo_routes.router)
api_router.include_router(averia_routes.router)
api_router.include_router(seleccion_taller_routes.router)
api_router.include_router(orden_routes.router)
api_router.include_router(asignacion_routes.router)
api_router.include_router(presupuesto_routes.router)
api_router.include_router(pago_routes.router)
api_router.include_router(notificacion_routes.router)
api_router.include_router(calificacion_routes.router)
api_router.include_router(factura_routes.router)
api_router.include_router(chat_routes.router)
api_router.include_router(operacion_routes.router)
api_router.include_router(comision_routes.router)
api_router.include_router(disponibilidad_routes.router)
api_router.include_router(push_routes.router)
api_router.include_router(catalogo_routes.router)
api_router.include_router(metrica_routes.router)

app.include_router(api_router)

register_error_handlers(app)

# ✅ Metadata de modelos
Base.metadata.create_all(bind=engine)
