import math
import time
import re
import pandas as pd
import bcrypt
from pydantic import  validator
from pydantic_settings import BaseSettings
from typing import Set, Optional

# --- Configuración Inicial---

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
    hashed_value: Optional[str] = None
    strength: Optional[str] = None
    crack_time_seconds: Optional[float] = None
    entropy: Optional[float] = None

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
        """
        Hashea una contraseña usando bcrypt.
        Bcrypt tiene un límite de 72 bytes, por lo que truncamos si es necesario.
        """
        # Convertir a bytes y truncar a 72 bytes si es necesario
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncar a 72 bytes de manera segura
            password_bytes = password_bytes[:72]
            # Decodificar de vuelta a string, manejando posibles caracteres cortados
            try:
                plain_password = password_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # Si hay un error de decodificación, truncar un byte más y volver a intentar
                plain_password = password_bytes[:-1].decode('utf-8', errors='ignore')
            password_bytes = plain_password.encode('utf-8')
        
        # Hashear usando bcrypt directamente
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @classmethod
    def from_hash(cls, hashed_value: str) -> 'Password':
        """
        Crea un objeto Password desde un hash existente (útil al leer de la BD).
        No valida la contraseña original ni calcula métricas.
        """
        # Usar model_construct para crear instancia sin validación
        return cls.model_construct(
            value="",  # No tenemos el texto plano
            hashed_value=hashed_value,
            strength="N/A",  # Valor por defecto
            crack_time_seconds=0.0,  # Valor por defecto
            entropy=0.0  # Valor por defecto
        )

    def verify_password(self, plain_password: str) -> bool:
        """
        Verifica una contraseña en texto plano contra el hash almacenado.
        Trunca la contraseña a 72 bytes para coincidir con el límite de bcrypt.
        """
        # Truncar la contraseña a 72 bytes si es necesario (igual que al hashear)
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            try:
                plain_password = password_bytes.decode('utf-8')
            except UnicodeDecodeError:
                plain_password = password_bytes[:-1].decode('utf-8', errors='ignore')
            password_bytes = plain_password.encode('utf-8')
        
        # Verificar usando bcrypt directamente
        return bcrypt.checkpw(password_bytes, self.hashed_value.encode('utf-8'))