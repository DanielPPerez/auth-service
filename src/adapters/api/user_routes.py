from fastapi import APIRouter, HTTPException, status, Depends
import uuid
from sqlalchemy.orm import Session
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
def register_user(
    request: RegisterUserRequestDTO, 
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
):
    """
    Endpoint para registrar un nuevo usuario.
    """
    try:
        user_response = use_case.execute(request)
        return user_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrió un error inesperado: {e}")

@router.post("/login", response_model=LoginResponseDTO)
def login(
    request: LoginRequestDTO,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case)
):
    try:
        return use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/users/{user_id}", response_model=UserDetailResponseDTO)
def get_user(
    user_id: uuid.UUID,
    use_case: GetUserUseCase = Depends(get_user_use_case)
):
    try:
        return use_case.execute(user_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/users/{user_id}", response_model=UserDetailResponseDTO)
def update_user(
    user_id: uuid.UUID, 
    request: UpdateUserRequestDTO,
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case)
):
    try:
        update_data = request.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron datos para actualizar.")
            
        validated_request = UpdateUserRequestDTO(**update_data)
        return use_case.execute(user_id, validated_request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case)
):
    try:
        use_case.execute(user_id)
        return # FastAPI manejará la respuesta 204
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))