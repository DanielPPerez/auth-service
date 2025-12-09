from fastapi import APIRouter, HTTPException, status, Depends, Request, Header, Response
from typing import Optional
import uuid
from sqlalchemy.orm import Session
from src.adapters.api.rate_limiter import limiter, REGISTER_LIMIT, LOGIN_LIMIT
from src.adapters.api.security import get_current_user_id_from_context
# Importaciones de Casos de Uso
from src.use_cases.register_user import RegisterUserUseCase
from src.use_cases.login_user import LoginUserUseCase
from src.use_cases.get_user import GetUserUseCase
from src.use_cases.update_user import UpdateUserUseCase
from src.use_cases.delete_user import DeleteUserUseCase
# Importaciones de DTOs
from src.use_cases.dtos import (
    RegisterUserRequestDTO, UserResponseDTO, LoginRequestDTO, LoginResponseDTO,
    UserDetailResponseDTO, UpdateUserRequestDTO
)
# Importación del Repositorio
from src.adapters.repositories.user_repository import InMemoryUserRepository
from src.adapters.repositories.mysql_user_repository import MySQLUserRepository
from src.adapters.repositories.database import get_db

# --- Creación del Router ---
router = APIRouter(
    tags=["Usuarios y Autenticación"] 
)


# --- Inyección de Dependencias ---

def get_user_repository(db: Session = Depends(get_db)) -> MySQLUserRepository:
    return MySQLUserRepository(db=db)

# Actualiza las funciones "get_use_case" para que dependan del repositorio
def get_register_user_use_case(
    repo: MySQLUserRepository = Depends(get_user_repository)
) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repository=repo)

def get_login_user_use_case(
    repo: MySQLUserRepository = Depends(get_user_repository)
) -> LoginUserUseCase:
    return LoginUserUseCase(user_repository=repo)

def get_update_user_use_case(
    repo: MySQLUserRepository = Depends(get_user_repository)
    ) -> UpdateUserUseCase:
    return UpdateUserUseCase(user_repository=repo)

def get_delete_user_use_case(repo: MySQLUserRepository = Depends(get_user_repository)
    ) -> DeleteUserUseCase:
    return DeleteUserUseCase(user_repository=repo)

def get_user_use_case(
    repo: MySQLUserRepository = Depends(get_user_repository)
) -> GetUserUseCase:
    return GetUserUseCase(user_repository=repo)

def get_db_user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


# --- Definición de Endpoints ---
# Nota que ahora usamos `@router.post`, `@router.get`, etc., en lugar de `@app.*`

# Línea correcta
@router.post("/register", response_model=UserResponseDTO, status_code=status.HTTP_201_CREATED)
@limiter.limit(REGISTER_LIMIT)
def register_user(
    request: Request,
    register_request: RegisterUserRequestDTO, 
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    """
    Endpoint para registrar un nuevo usuario.
    
    Validaciones aplicadas:
    - Email: formato RFC 5321, longitud 5-254 caracteres, sanitización
    - Password: longitud 8-128 caracteres, complejidad, diccionario de contraseñas comunes
    - Username: longitud 3-30 caracteres, formato alfanumérico, sanitización
    - Confirmación de contraseña: debe coincidir con la contraseña original
    - Sanitización de todos los campos de texto
    """
    try:
        # Sanitización adicional de campos de texto (aunque ya se hace en los Value Objects)
        # Esto proporciona una capa adicional de defensa en profundidad
        if hasattr(register_request, 'username') and register_request.username:
            register_request.username = register_request.username.strip()
        if hasattr(register_request, 'email') and register_request.email:
            register_request.email = register_request.email.strip()
        
        # Ejecutar el caso de uso que aplicará todas las validaciones
        user_response = use_case.execute(register_request)
        return user_response
    except ValueError as e:
        # Errores de validación de negocio (Value Objects, duplicados, etc.)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # No exponer detalles del error interno por seguridad
        # Los logs detallados se envían al servicio de monitoreo
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Ocurrió un error inesperado al procesar la solicitud"
        )

@router.post("/login", response_model=LoginResponseDTO)
@limiter.limit(LOGIN_LIMIT)
def login(
    request: Request,
    login_request: LoginRequestDTO,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case)
):
    try:
        return use_case.execute(login_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/users/{user_id}", response_model=UserDetailResponseDTO)
def get_user(
    user_id: uuid.UUID,
    context_user_id: uuid.UUID = Depends(get_current_user_id_from_context),
    use_case: GetUserUseCase = Depends(get_user_use_case)
):
    """
    Obtiene los detalles de un usuario.
    Valida que el usuario solo pueda ver sus propios datos (validación contextual).
    """
    # Validación contextual: solo puede ver sus propios datos
    if user_id != context_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los datos de otro usuario."
        )
    
    try:
        return use_case.execute(user_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el usuario"
        )

@router.put("/users/{user_id}", response_model=UserDetailResponseDTO)
def update_user(
    user_id: uuid.UUID, 
    request: UpdateUserRequestDTO,
    context_user_id: uuid.UUID = Depends(get_current_user_id_from_context),
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case)
):
    """
    Actualiza la información de un usuario.
    Valida que el usuario solo pueda actualizar sus propios datos (validación contextual).
    """
    # Validación contextual: solo puede actualizar sus propios datos
    if user_id != context_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar los datos de otro usuario."
        )
    """
    Endpoint para actualizar información de un usuario.
    Aplica sanitización a los campos de texto antes de procesar.
    """
    try:
        # Sanitización de campos de texto antes de procesar
        update_data = request.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron datos para actualizar.")
        
        # Sanitizar campos de texto si existen
        if 'username' in update_data and update_data['username']:
            update_data['username'] = update_data['username'].strip()
            
        validated_request = UpdateUserRequestDTO(**update_data)
        return use_case.execute(user_id, validated_request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # No exponer detalles del error interno
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al procesar la solicitud"
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    context_user_id: uuid.UUID = Depends(get_current_user_id_from_context),
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case)
):
    """
    Elimina un usuario.
    Valida que el usuario solo pueda eliminar su propia cuenta (validación contextual).
    """
    # Validación contextual: solo puede eliminar su propia cuenta
    if user_id != context_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar la cuenta de otro usuario."
        )
    
    try:
        use_case.execute(user_id)
        return # FastAPI manejará la respuesta 204
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el usuario"
        )

@router.get("/validate-token")
def validate_token(
    authorization: Optional[str] = Header(None)
):
    """
    Endpoint interno usado por el API Gateway para validar JWT y extraer user_id.
    Retorna el user_id en el header X-User-Id para que nginx lo capture.
    
    Este endpoint permite que el gateway valide el JWT y extraiga el user_id
    sin que los microservicios tengan que decodificar el token nuevamente.
    """
    if not authorization or not authorization.startswith("Bearer "):
        response = Response(status_code=401)
        return response
    
    token = authorization.split(" ")[1]
    try:
        from jose import JWTError, jwt
        from src.config import settings
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        
        if not user_id:
            response = Response(status_code=401)
            return response
        
        # Retornar respuesta con header X-User-Id para que nginx lo capture
        response = Response(status_code=200)
        response.headers["X-User-Id"] = user_id
        return response
        
    except JWTError:
        response = Response(status_code=401)
        return response