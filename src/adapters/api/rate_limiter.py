"""
Rate limiting para proteger endpoints críticos contra abuso.
Implementa límites de velocidad según OWASP recomendaciones.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Inicializar el rate limiter
limiter = Limiter(key_func=get_remote_address)

# Configuración de límites por endpoint
# Estos límites son conservadores y pueden ajustarse según necesidades

# Límites para registro de usuarios (más restrictivo)
REGISTER_LIMIT = "5/minute"  # Máximo 5 registros por minuto por IP

# Límites para login (más restrictivo para prevenir fuerza bruta)
LOGIN_LIMIT = "10/minute"  # Máximo 10 intentos de login por minuto por IP

# Límites para otros endpoints
GENERAL_LIMIT = "100/minute"  # Límite general para otros endpoints

