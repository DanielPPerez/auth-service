from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from src.domain.value_objects.enums import Entorno, NivelEducativo, Rol

class RegisterUserRequestDTO(BaseSettings):
    username: str
    email: str
    password: str
    age: int
    entorno: Entorno
    nivel_educativo: NivelEducativo

class UserResponseDTO(BaseSettings):
    user_id: str
    username: str
    email: str
    message: str
    
# --- DTOs para Respuestas ---
class ProfileResponseDTO(BaseSettings):
    rol: Rol
    entorno: Entorno
    nivel_educativo: NivelEducativo

class UserDetailResponseDTO(BaseSettings): # DTO más completo para respuestas
    user_id: str
    username: str
    email: str
    age: int
    profile: ProfileResponseDTO

# --- DTOs para Login ---
class LoginRequestDTO(BaseSettings):
    email: str
    password: str

class LoginResponseDTO(BaseSettings):
    access_token: str
    token_type: str = "bearer"

# --- DTOs para Update ---
class UpdateUserRequestDTO(BaseSettings):
    username: Optional[str] = Field(None, min_length=3)
    age: Optional[int] = Field(None, gt=17) # gt = greater than
    entorno: Optional[Entorno] = None
    nivel_educativo: Optional[NivelEducativo] = None