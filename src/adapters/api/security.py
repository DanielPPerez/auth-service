# src/adapters/api/security.py
import uuid
from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from jose import JWTError, jwt
from src.config import settings

def get_current_user_id_from_context(
    x_user_context: Optional[str] = Header(None, alias="X-User-Context")
) -> uuid.UUID:
    """
    Obtiene el user_id del header X-User-Context adjuntado por el API Gateway.
    
    El API Gateway valida el JWT y adjunta este header, por lo que confiamos
    en él sin necesidad de decodificar el JWT nuevamente (mTLS trust).
    
    Args:
        x_user_context: Header X-User-Context con el user_id (UUID como string)
        
    Returns:
        UUID del usuario
        
    Raises:
        HTTPException: Si el header no está presente o es inválido
    """
    if not x_user_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header X-User-Context no presente. El request debe pasar por el API Gateway.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = uuid.UUID(x_user_context)
        return user_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El valor del header X-User-Context no es un UUID válido."
        )


def get_current_user_id(
    x_user_context: Optional[str] = Header(None, alias="X-User-Context"),
    authorization: Optional[str] = Header(None)
) -> uuid.UUID:
    """
    Obtiene el user_id del header X-User-Context (preferido) o del JWT (fallback).
    
    Prioriza el header X-User-Context si está presente (confianza en gateway),
    de lo contrario decodifica el JWT directamente (útil para desarrollo/testing).
    """
    # Prioridad 1: Header X-User-Context (confianza en gateway - producción)
    if x_user_context:
        try:
            return uuid.UUID(x_user_context)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El valor del header X-User-Context no es un UUID válido."
            )
    
    # Prioridad 2: Decodificar JWT directamente (fallback para desarrollo/testing)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id_str = payload.get("sub")
            if user_id_str is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token JWT inválido: falta 'sub'",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return uuid.UUID(user_id_str)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token JWT inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ID de usuario en el token es inválido."
            )
    
    # Si no hay ni header ni token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticación requerida. Proporciona un token JWT válido o asegúrate de pasar por el API Gateway.",
        headers={"WWW-Authenticate": "Bearer"},
    )

