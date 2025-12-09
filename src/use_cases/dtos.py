from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
import re
from src.domain.value_objects.enums import Entorno, NivelEducativo, Rol

class RegisterUserRequestDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Nombre de usuario entre 3 y 30 caracteres")
    email: EmailStr = Field(..., description="Correo electrónico válido")
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña entre 8 y 128 caracteres")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Confirmación de contraseña")
    age: int = Field(..., ge=1, le=120, description="Edad entre 1 y 120 años")
    entorno: Entorno
    nivel_educativo: NivelEducativo

    @validator('password')
    def validate_password(cls, v):
        """
        Valida la política de contraseñas según MSTG-AUTH-5:
        - Mínimo 8 caracteres (validado explícitamente)
        - Máximo 128 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        """
        # Sanitización: trim de espacios
        if isinstance(v, str):
            v = v.strip()
        
        # Validación explícita de longitud mínima
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        # Validación explícita de longitud máxima
        if len(v) > 128:
            raise ValueError('La contraseña no puede tener más de 128 caracteres')
        
        # Validación explícita de al menos 1 mayúscula
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        
        # Validación explícita de al menos 1 minúscula
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        
        # Validación explícita de al menos 1 número
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        """
        Valida que la confirmación de contraseña coincida con la contraseña original.
        """
        # Sanitización: trim de espacios
        if isinstance(v, str):
            v = v.strip()
        
        # Validar que coincida con la contraseña original
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """
        Valida que el username cumpla con las reglas básicas.
        La validación completa se hace en el Value Object Username.
        """
        # Sanitización: trim de espacios
        if isinstance(v, str):
            v = v.strip()
        
        # Validación básica de espacios (validación completa en Value Object)
        if ' ' in v:
            raise ValueError('El nombre de usuario no puede contener espacios')
        
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """
        Sanitiza el email antes de la validación.
        La validación completa se hace en el Value Object Email.
        """
        # Sanitización: trim de espacios
        if isinstance(v, str):
            v = v.strip()
        return v

class UserResponseDTO(BaseModel):
    user_id: str
    username: str
    email: str
    message: str
    
# --- DTOs para Respuestas ---
class ProfileResponseDTO(BaseModel):
    rol: Rol
    entorno: Entorno
    nivel_educativo: NivelEducativo

class UserDetailResponseDTO(BaseModel): # DTO más completo para respuestas
    user_id: str
    username: str
    email: str
    age: int
    profile: ProfileResponseDTO

# --- DTOs para Login ---
class LoginRequestDTO(BaseModel):
    email: str
    password: str

class LoginResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- DTOs para Update ---
class UpdateUserRequestDTO(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    age: Optional[int] = Field(None, gt=17) # gt = greater than
    entorno: Optional[Entorno] = None
    nivel_educativo: Optional[NivelEducativo] = None