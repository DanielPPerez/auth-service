# src/use_cases/update_user.py
import uuid
from src.ports.repositories.user_repository import IUserRepository
from src.domain.value_objects.username import Username
from .dtos import UpdateUserRequestDTO, UserDetailResponseDTO, ProfileResponseDTO

class UpdateUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: uuid.UUID, request: UpdateUserRequestDTO) -> UserDetailResponseDTO:
        """
        Actualiza la información de un usuario con validaciones robustas.
        Usa Value Objects para validar username antes de actualizar.
        """
        user_to_update = self.user_repository.find_by_id(user_id)
        if not user_to_update:
            raise FileNotFoundError("Usuario no encontrado.")

        # Validar username usando Value Object si se proporciona
        validated_username = None
        if request.username:
            try:
                username_vo = Username(value=request.username)
                validated_username = username_vo.value
            except ValueError as e:
                raise e
            
            # Validar que el nuevo username no esté en uso por otro usuario
            if validated_username != user_to_update.username:
                if self.user_repository.find_by_username(validated_username):
                    raise ValueError("El nombre de usuario ya está en uso.")
        else:
            validated_username = request.username

        # Usar los métodos de la entidad para actualizarse
        user_to_update.update_details(username=validated_username, age=request.age)
        user_to_update.update_profile(entorno=request.entorno, nivel_educativo=request.nivel_educativo)
        
        self.user_repository.update(user_to_update)

        # Devolver el usuario actualizado
        return UserDetailResponseDTO(
            user_id=str(user_to_update.user_id),
            username=user_to_update.username,
            email=user_to_update.email.value,
            age=user_to_update.age,
            profile=ProfileResponseDTO(**user_to_update.profile.dict())
        )