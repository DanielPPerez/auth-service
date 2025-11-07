import uuid
from pydantic import Field
from pydantic_settings import BaseSettings
from src.domain.value_objects.enums import Rol, Entorno, NivelEducativo

class Profile(BaseSettings):
  profile_id: uuid.UUID = Field(default_factory=uuid.uuid4)
  user_id: uuid.UUID
  rol: Rol = Rol.ALUMNO
  entorno: Entorno
  nivel_educativo: NivelEducativo
