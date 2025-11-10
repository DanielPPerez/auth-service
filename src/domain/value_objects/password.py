import math
import re
import pandas as pd
import bcrypt
from pydantic import BaseModel
from typing import Set, Optional

COMMON_PASSWORDS: Set[str] = set()
try:
    df = pd.read_csv('1millionPasswords.csv', header=None, usecols=[1], low_memory=False)
    COMMON_PASSWORDS = set(df[1].dropna().astype(str))
    print(f"Cargadas {len(COMMON_PASSWORDS)} contraseñas comunes del diccionario.")
except FileNotFoundError:
    print("Advertencia: No se encontró '1millionPasswords.csv'. La verificación de diccionario no funcionará.")
except Exception as e:
    print(f"Error al cargar el diccionario de contraseñas: {e}")


class Password(BaseModel):
    value: str
    hashed_value: Optional[str] = None
    strength: Optional[str] = None
    crack_time_seconds: Optional[float] = None
    entropy: Optional[float] = None

    class Config:
        validate_assignment = True
        
    def __init__(self, **data):
        if 'value' in data and 'hashed_value' not in data:
            plain_password = data['value']
            self._validate_password(plain_password)
            entropy = self._calculate_entropy(plain_password)
            data['entropy'] = entropy
            data['strength'] = self._get_strength_category(entropy)
            data['crack_time_seconds'] = self._calculate_crack_time(entropy)
            data['hashed_value'] = self._hash_password(plain_password)
        super().__init__(**data)

    def _validate_password(self, plain_password: str):
        """Valida que la contraseña no esté en el diccionario de contraseñas comunes."""
        if plain_password in COMMON_PASSWORDS:
            raise ValueError("La contraseña es demasiado común.")

    def _calculate_entropy(self, password: str) -> float:
        """Calcula la entropía de la contraseña."""
        pool_size = self._get_character_pool_size(password)
        return math.log2(pool_size ** len(password)) if pool_size > 0 else 0

    def _calculate_crack_time(self, entropy: float) -> float:
        """Calcula el tiempo estimado para crackear la contraseña."""
        ATTEMPTS_PER_SECOND = 10**11
        return (2**entropy) / ATTEMPTS_PER_SECOND

    @staticmethod
    def _get_character_pool_size(password: str) -> int:
        pool = 0
        if re.search(r'[a-z]', password): pool += 26
        if re.search(r'[A-Z]', password): pool += 26
        if re.search(r'[0-9]', password): pool += 10
        if re.search(r'[^a-zA-Z0-9]', password): pool += 32
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
        """Hashea una contraseña usando bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @classmethod
    def construct(cls, hashed_value: str):
        """Método para crear un Password solo con el hash (para cuando se lee de la BD)"""
        return cls(hashed_value=hashed_value, value="")

    def verify_password(self, plain_password: str) -> bool:
        """Verifica una contraseña en texto plano contra el hash almacenado."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            self.hashed_value.encode('utf-8')
        )