import uuid
from src.ports.repositories.user_repository import IUserRepository
from .dtos import UserDetailResponseDTO, ProfileResponseDTO

class GetUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: uuid.UUID) -> UserDetailResponseDTO:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise FileNotFoundError("Usuario no encontrado.")

        return UserDetailResponseDTO(
            user_id=str(user.user_id),
            username=user.username,
            email=user.email.value,
            age=user.age,
            profile=ProfileResponseDTO(**user.profile.dict())
        )