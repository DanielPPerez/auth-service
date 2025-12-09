import re
from pydantic import validator
from pydantic_settings import BaseSettings

class Email(BaseSettings):
    value: str

    @validator('value')
    def email_must_be_valid(cls, v):
        """
        Valida un email según RFC 5321:
        - Longitud mínima: 5 caracteres (ejemplo mínimo: a@b.c)
        - Longitud máxima: 254 caracteres (RFC 5321)
        - Formato válido con regex robusta
        - Sanitización: trim de espacios
        - Validación de caracteres peligrosos
        """
        # Sanitización: trim de espacios
        if isinstance(v, str):
            v = v.strip()
        else:
            v = str(v).strip()
        
        # Validación de longitud según RFC 5321
        if len(v) < 5:
            raise ValueError('El email debe tener al menos 5 caracteres')
        if len(v) > 254:
            raise ValueError('El email no puede tener más de 254 caracteres')
        
        # Validación de caracteres peligrosos adicionales
        dangerous_chars = ['<', '>', '"', "'", '\\', '/', ';', ':', '&', '|', '`']
        if any(char in v for char in dangerous_chars):
            raise ValueError('El email contiene caracteres no permitidos')
        
        # Validación de formato con regex robusta
        # Permite: letras, números, puntos, guiones bajos, porcentajes, signos más, guiones
        # Requiere: símbolo @ obligatorio, dominio válido, extensión de al menos 2 caracteres
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex, v):
            raise ValueError('Formato de email inválido')
        
        # Validación adicional: no puede empezar o terminar con punto o guión
        local_part, domain_part = v.split('@', 1)
        if local_part.startswith('.') or local_part.endswith('.') or local_part.startswith('-') or local_part.endswith('-'):
            raise ValueError('El email contiene caracteres inválidos en la parte local')
        if domain_part.startswith('.') or domain_part.endswith('.') or domain_part.startswith('-') or domain_part.endswith('-'):
            raise ValueError('El email contiene caracteres inválidos en el dominio')
        
        return v