# src/adapters/repositories/user_repository.py
from typing import Dict, Optional, List
import uuid
from src.ports.repositories.user_repository import IUserRepository
from src.domain.entities.user import User

class InMemoryUserRepository(IUserRepository):
    
    def __init__(self):
        self._users: Dict[uuid.UUID, User] = {}

    def save(self, user: User) -> None:
        print(f"Guardando usuario {user.username} en memoria.")
        self._users[user.user_id] = user

    # --- MÉTODO FALTANTE AÑADIDO AQUÍ ---
    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        print(f"Buscando usuario con ID {user_id} en memoria.")
        # .get() es perfecto aquí porque devuelve None si la clave no existe,
        # lo que coincide con nuestro tipo de retorno Optional[User].
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        for user in self._users.values():
            if user.email.value == email:
                return user
        return None

    def find_by_username(self, username: str) -> Optional[User]:
        for user in self._users.values():
            if user.username == username:
                return user
        return None
        
    def find_all(self) -> List[User]:
        return list(self._users.values())

    def update(self, user: User) -> None:
        if user.user_id in self._users:
            print(f"Actualizando usuario {user.username} en memoria.")
            self._users[user.user_id] = user
        else:
            # En un caso real, podrías lanzar un error aquí.
            # raise FileNotFoundError("Usuario no encontrado para actualizar.")
            pass # Por ahora lo dejamos pasar

    def delete(self, user_id: uuid.UUID) -> None:
        if user_id in self._users:
            print(f"Eliminando usuario con ID {user_id} de la memoria.")
            del self._users[user_id]
        else:
            # En un caso real, podrías lanzar un error aquí.
            # raise FileNotFoundError("Usuario no encontrado para eliminar.")
            pass # Por ahora lo dejamos pasar