# src/adapters/repositories/mysql_user_repository.py
from typing import Optional, List
import uuid
from sqlalchemy.orm import Session, joinedload
from src.ports.repositories.user_repository import IUserRepository
from src.domain.entities.user import User
from src.domain.entities.profile import Profile
from src.domain.value_objects.email import Email
from src.domain.value_objects.password import Password
from src.adapters.repositories.db_models import UserDB, ProfileDB

# Importa los modelos de la base de datos (la representación en la tabla)
from .db_models import UserDB, ProfileDB

class MySQLUserRepository(IUserRepository):
    
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> None:
        user_model = self._entity_to_model(user)
        self.db.add(user_model)
        self.db.commit()

    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        user_model = self.db.query(UserDB).options(joinedload(UserDB.profile)).filter(UserDB.user_id == user_id).first()
        return self._model_to_entity(user_model) if user_model else None

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
        user_model = self.db.query(UserDB).filter(UserDB.user_id == user.user_id).first()
        if user_model:
            # Actualizar campos
            user_model.username = user.username
            user_model.age = user.age
            user_model.profile.entorno = user.profile.entorno
            user_model.profile.nivel_educativo = user.profile.nivel_educativo
            self.db.commit()
    
    def delete(self, user_id: uuid.UUID) -> None:
        user_model = self.db.query(UserDB).filter(UserDB.user_id == user_id).first()
        if user_model:
            self.db.delete(user_model)
            self.db.commit()

    # --- Mappers privados para convertir entre Entidad de Dominio y Modelo ORM ---
    def _model_to_entity(self, model: UserDB) -> User:
        # Reconstruye el objeto de valor Password sin el texto plano
        password_vo = Password.construct(hashed_value=model.password_hash)
        
        profile_entity = Profile(
            profile_id=model.profile.profile_id,
            user_id=model.user_id,
            rol=model.profile.rol,
            entorno=model.profile.entorno,
            nivel_educativo=model.profile.nivel_educativo
        )
        
        user_entity = User(
            user_id=model.user_id,
            username=model.username,
            age=model.age,
            email=Email(value=model.email),
            password=password_vo,
            profile=profile_entity,
            created_at=model.created_at
        )
        return user_entity

    def _map_entity_to_db_model(self, user: User) -> UserDB:
        """Convierte una entidad de dominio a un modelo SQLAlchemy."""
        profile_db = ProfileDB(
            profile_id=str(user.profile.profile_id),
            user_id=str(user.user_id),
            rol=user.profile.rol,
            entorno=user.profile.entorno,
            nivel_educativo=user.profile.nivel_educativo
        )
        
        user_db = UserDB(
            user_id=str(user.user_id),
            username=user.username,
            email=user.email.value,
            password_hash=user.password.hashed_value,
            age=user.age,
            created_at=user.created_at,
            profile=profile_db
        )
        return user_db