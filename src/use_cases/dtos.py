from pydantic import BaseModel, Field
from typing import Optional
from src.domain.value_objects.enums import Entorno, NivelEducativo, Rol

class RegisterUserRequestDTO(BaseModel):
    username: str
    email: str
    password: str
    age: int
    entorno: Entorno
    nivel_educativo: NivelEducativo


class UserResponseDTO(BaseModel):
    user_id: str
    username: str
    email: str
    message: str


class ProfileResponseDTO(BaseModel):
    rol: Rol
    entorno: Entorno
    nivel_educativo: NivelEducativo


class UserDetailResponseDTO(BaseModel):
    user_id: str
    username: str
    email: str
    age: int
    profile: ProfileResponseDTO


class LoginRequestDTO(BaseModel):
    email: str
    password: str


class LoginResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UpdateUserRequestDTO(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    age: Optional[int] = Field(None, gt=17)
    entorno: Optional[Entorno] = None
    nivel_educativo: Optional[NivelEducativo] = None