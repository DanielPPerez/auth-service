# src/config.py
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # Database
    db_host: str
    db_user: str
    db_password: str
    db_name: str
    db_port: int

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    def get_db_url(self) -> str:
        """Genera la URL de conexión para SQLAlchemy."""
        # Codificar usuario y contraseña para manejar caracteres especiales
        encoded_user = quote_plus(self.db_user)
        encoded_password = quote_plus(self.db_password)
        return f"mysql+pymysql://{encoded_user}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"

# Instancia única que será usada en toda la aplicación
settings = Settings()