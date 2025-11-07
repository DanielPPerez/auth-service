from abc import ABC, abstractmethod
from typing import Optional, List
import uuid
from src.domain.entities.user import User

class IUserRepository(ABC):
    
    @abstractmethod
    def save(self, user: User) -> None:
        """Guarda un usuario en el repositorio."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por su email."""
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Busca un usuario por su nombre de usuario."""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]: 
        """Busca un usuario por su ID."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[User]: 
        """Devuelve todos los usuarios."""
        pass
        
    @abstractmethod
    def update(self, user: User) -> None: 
        """Actualiza un usuario existente."""
        pass

    @abstractmethod
    def delete(self, user_id: uuid.UUID) -> None: 
        """Elimina un usuario por su ID."""
        pass