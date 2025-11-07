import math
import time
import re
import pandas as pd
from passlib.context import CryptContext
from pydantic import  validator
from pydantic_settings import BaseSettings
from typing import Set

# --- Configuración Inicial---

# 1. Configurar el contexto de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. Cargar y limpiar el diccionario de contraseñas predecibles
COMMON_PASSWORDS: Set[str] = set()
try:
    df = pd.read_csv('1millionPasswords.csv', header=None, usecols=[1], low_memory=False)
    COMMON_PASSWORDS = set(df[1].dropna().astype(str))
    print(f"Cargadas {len(COMMON_PASSWORDS)} contraseñas comunes del diccionario.")
except FileNotFoundError:
    print("Advertencia: No se encontró 'common_passwords.csv'. La verificación de diccionario no funcionará.")
except Exception as e:
    print(f"Error al cargar el diccionario de contraseñas: {e}")


class Password(BaseSettings):
    value: str # La contraseña en texto plano, solo existirá momentáneamente
    hashed_value: str = None
    strength: str = None
    crack_time_seconds: float = None
    entropy: float = None

    class Config:
        validate_assignment = True # Permite revalidar al asignar un valor
        
    def __init__(self, **data):
        super().__init__(**data)
        self._validate_and_process(self.value)
        self.hashed_value = self._hash_password(self.value)

    def _validate_and_process(self, plain_password: str):
        # Validación de diccionario
        if plain_password in COMMON_PASSWORDS:
            raise ValueError("La contraseña es demasiado común.")

        # Cálculo de entropía
        pool_size = self._get_character_pool_size(plain_password)
        self.entropy = math.log2(pool_size ** len(plain_password)) if pool_size > 0 else 0

        # Asignación de fuerza
        self.strength = self._get_strength_category(self.entropy)

        # Cálculo de tiempo de crackeo
        ATTEMPTS_PER_SECOND = 10**11 # 100 billones por segundo
        self.crack_time_seconds = (2**self.entropy) / ATTEMPTS_PER_SECOND

    @staticmethod
    def _get_character_pool_size(password: str) -> int:
        pool = 0
        if re.search(r'[a-z]', password): pool += 26
        if re.search(r'[A-Z]', password): pool += 26
        if re.search(r'[0-9]', password): pool += 10
        if re.search(r'[^a-zA-Z0-9]', password): pool += 32 # Símbolos comunes
        return pool

    @staticmethod
    def _get_strength_category(entropy: float) -> str:
        if entropy < 40: return "Muy Débil"
        if entropy < 60: return "Débil"
        if entropy < 80: return "Moderada"
        if entropy < 100: return "Fuerte"
        return "Muy Fuerte"

    @staticmethod
    def _hash_password(plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        """Verifica una contraseña en texto plano contra el hash almacenado."""
        return pwd_context.verify(plain_password, self.hashed_value)