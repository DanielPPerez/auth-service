# src/adapters/api/main.py
from fastapi import FastAPI
from src.adapters.api import user_routes
from src.adapters.repositories.database import engine, Base
from src.adapters.repositories import db_models

# --- Función para crear tablas ---
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# --- Evento de Inicio ---
# Esta es la línea que hay que corregir.
# Reemplaza los '...' por los argumentos de configuración de la app.
app = FastAPI(
    title="Servicio de Autenticación - Scriptoria AI",
    description="Microservicio para gestionar usuarios y autenticación.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    print("La aplicación está iniciando... Creando tablas de la base de datos si es necesario.")
    create_db_and_tables()

# --- Inclusión de Rutas ---
app.include_router(user_routes.router)

# --- Endpoints de Nivel de Aplicación ---
@app.get("/health", tags=["Monitoring"])
def health_check():
    """
    Verifica que el servicio esté funcionando correctamente.
    """
    # Se debe importar 'status' para usarlo aquí
    from fastapi import status
    return {"status": "ok"}