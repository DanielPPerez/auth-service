import uuid
from src.ports.repositories.user_repository import IUserRepository

class DeleteUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: uuid.UUID) -> None:
        user_to_delete = self.user_repository.find_by_id(user_id)
        if not user_to_delete:
            raise FileNotFoundError("Usuario no encontrado.")
        
        self.user_repository.delete(user_id)