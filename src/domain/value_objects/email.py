import re
from pydantic import  validator
from pydantic_settings import BaseSettings

class Email(BaseSettings):
    value: str

    @validator('value')
    def email_must_be_valid(cls, v):
        # Expresión regular simple para validar email
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex, v):
            raise ValueError('Formato de email inválido')
        return v