import re
from pydantic import validator
from pydantic_settings import BaseSettings

class Username(BaseSettings):
    """
    Value Object para nombres de usuario con validaciones robustas:
    - Longitud: 3-30 caracteres
    - Sin espacios
    - Solo caracteres alfanuméricos, guiones bajos y guiones
    - No puede empezar o terminar con guión o guión bajo
    - Sanitización: trim de espacios
    """
    value: str

    @validator('value')
    def username_must_be_valid(cls, v):
        """
        Valida que el nombre de usuario cumpla con todas las reglas de seguridad.
        """
        # Sanitización: trim de espacios
        if isinstance(v, str):
            v = v.strip()
        else:
            v = str(v).strip()
        
        # Validación de longitud mínima
        if len(v) < 3:
            raise ValueError('El nombre de usuario debe tener al menos 3 caracteres')
        
        # Validación de longitud máxima
        if len(v) > 30:
            raise ValueError('El nombre de usuario no puede tener más de 30 caracteres')
        
        # Validación de espacios
        if ' ' in v:
            raise ValueError('El nombre de usuario no puede contener espacios')
        
        # Whitelisting: solo caracteres alfanuméricos, guiones bajos y guiones
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El nombre de usuario solo puede contener letras, números, guiones bajos (_) y guiones (-)')
        
        # No puede empezar o terminar con guión o guión bajo
        if v.startswith('-') or v.startswith('_'):
            raise ValueError('El nombre de usuario no puede empezar con guión (-) o guión bajo (_)')
        if v.endswith('-') or v.endswith('_'):
            raise ValueError('El nombre de usuario no puede terminar con guión (-) o guión bajo (_)')
        
        # Validación adicional: no puede tener solo números
        if v.isdigit():
            raise ValueError('El nombre de usuario no puede contener solo números')
        
        return v

