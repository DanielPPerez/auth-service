from src.adapters.repositories.user_repository import IUserRepository
from src.domain.entities.user import User
from src.domain.entities.profile import Profile
from src.domain.value_objects.email import Email
from src.domain.value_objects.password import Password
from .dtos import RegisterUserRequestDTO, UserResponseDTO

class RegisterUserUseCase:
  def __init__(self, user_repository: IUserRepository):
    self.user_repository = user_repository

def execute(self, request: RegisterUserRequestDTO) -> UserResponseDTO:
    # 1. Validar que el usuario o email no existan
    if self.user_repository.find_by_email(request.email):
        raise ValueError("El email ya está en uso.")
    if self.user_repository.find_by_username(request.username):
        raise ValueError("El nombre de usuario ya está en uso.")

    # 2. Crear los objetos de valor y entidades
    try:
        email_vo = Email(value=request.email)
        password_vo = Password(value=request.password)
    except ValueError as e:
        raise e

    # 3. Crear el agregado completo
    user_entity = User(
        username=request.username,
        age=request.age,
        email=email_vo,
        password=password_vo
    )
    
    profile_entity = Profile(
        user_id=user_entity.user_id,
        entorno=request.entorno,
        nivel_educativo=request.nivel_educativo
    )
    
    user_entity.profile = profile_entity
    
    # 4. Guardar a través del repositorio
    self.user_repository.save(user_entity)

    # 5. Devolver una respuesta DTO
    return UserResponseDTO(
        user_id=str(user_entity.user_id),
        username=user_entity.username,
        email=user_entity.email.value,
        message="Usuario registrado exitosamente"
    )