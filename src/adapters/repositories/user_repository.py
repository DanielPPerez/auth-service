from typing import Dict, Optional, List
import uuid
from src.ports.repositories.user_repository import IUserRepository
from src.domain.entities.user import User


class InMemoryUserRepository(IUserRepository):
    
    def __init__(self):
        self._users: Dict[uuid.UUID, User] = {}

    def save(self, user: User) -> None:
        self._users[user.user_id] = user

    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
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
            self._users[user.user_id] = user

    def delete(self, user_id: uuid.UUID) -> None:
        if user_id in self._users:
            del self._users[user_id]