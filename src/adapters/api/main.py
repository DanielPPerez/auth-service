# src/adapters/api/main.py
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.adapters.api import user_routes
from src.adapters.repositories.database import engine, Base
from src.adapters.repositories import db_models
from src.adapters.api.rate_limiter import limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

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

# Configurar rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurar CORS para permitir peticiones desde cualquier origen
# En producción, deberías restringir esto a dominios específicos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios exactos
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

# Middleware de seguridad (MSTG-NETWORK-1)
# Solo acepta requests del API Gateway o hosts confiables
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "api.scriptoria.com",
        "localhost",
        "auth-service",
        "127.0.0.1",
        "auth-service-1-yr0s.onrender.com"  # Dominio de Render
    ]
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