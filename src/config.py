# src/config.py
from pydantic_settings import BaseSettings

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
        # Cambiamos 'mysqlclient' por 'pymysql'
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env" # Le dice a Pydantic que cargue las variables desde el archivo .env

# Instancia única que será usada en toda la aplicación
settings = Settings()