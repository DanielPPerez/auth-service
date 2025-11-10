from src.ports.repositories.user_repository import IUserRepository
from .dtos import LoginRequestDTO, LoginResponseDTO
from src.adapters.security import create_access_token 

class LoginUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, request: LoginRequestDTO) -> LoginResponseDTO:
        # Buscar al usuario por email
        user = self.user_repository.find_by_email(request.email)
        if not user:
            raise ValueError("Email o contraseña incorrectos.") 

        # Verificar la contraseña
        if not user.password.verify_password(request.password):
            raise ValueError("Email o contraseña incorrectos.")

        # Crear el token JWT
        access_token = create_access_token(data={"sub": str(user.user_id)})
        
        return LoginResponseDTO(access_token=access_token)