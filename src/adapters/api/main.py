from fastapi import FastAPI
from src.adapters.api import user_routes
from src.adapters.repositories.database import engine, Base
from src.adapters.repositories import db_models


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Servicio de Autenticación - Scriptoria AI",
    description="Microservicio para gestionar usuarios y autenticación.",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(user_routes.router)


@app.get("/health", tags=["Monitoring"])
def health_check():
    """
    Verifica que el servicio esté funcionando correctamente.
    """
    return {"status": "ok"}