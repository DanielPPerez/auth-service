import uuid
import datetime
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from src.domain.value_objects.email import Email
from src.domain.value_objects.password import Password
from src.domain.entities.profile import Profile
from src.domain.value_objects.enums import Entorno, NivelEducativo

class User(BaseSettings):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: str
    age: int
    email: Email
    password: Password
    profile: Optional[Profile] = None 
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True # Importante para que las actualizaciones validen

    def update_details(self, username: str = None, age: int = None):
        """Actualiza los detalles básicos del usuario."""
        if username:
            # Aquí podrías añadir validaciones de negocio, ej:
            if len(username) < 3:
                raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")
            self.username = username
        if age:
            if age < 18:
                raise ValueError("El usuario debe ser mayor de edad.")
            self.age = age

    def update_profile(self, entorno: Entorno = None, nivel_educativo: NivelEducativo = None):
        """Actualiza los detalles del perfil del usuario."""
        if not self.profile:
            raise ValueError("El usuario no tiene un perfil para actualizar.")
        if entorno:
            self.profile.entorno = entorno
        if nivel_educativo:
            self.profile.nivel_educativo = nivel_educativo