from typing import Optional, List
import uuid
from sqlalchemy.orm import Session, joinedload
from src.ports.repositories.user_repository import IUserRepository
from src.domain.entities.user import User
from src.domain.entities.profile import Profile
from src.domain.value_objects.email import Email
from src.domain.value_objects.password import Password
from src.adapters.repositories.db_models import UserDB, ProfileDB

class MySQLUserRepository(IUserRepository):
    
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User) -> None:
        user_model = self._map_entity_to_db_model(user)
        self.db.add(user_model)
        self.db.commit()

    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        user_model = self.db.query(UserDB).options(joinedload(UserDB.profile)).filter(UserDB.user_id == str(user_id)).first()
        return self._model_to_entity(user_model) if user_model else None

    def find_by_email(self, email: str) -> Optional[User]:
        user_model = self.db.query(UserDB).options(joinedload(UserDB.profile)).filter(UserDB.email == email).first()
        return self._model_to_entity(user_model) if user_model else None

    def find_by_username(self, username: str) -> Optional[User]:
        user_model = self.db.query(UserDB).options(joinedload(UserDB.profile)).filter(UserDB.username == username).first()
        return self._model_to_entity(user_model) if user_model else None
    
    def find_all(self) -> List[User]:
        user_models = self.db.query(UserDB).options(joinedload(UserDB.profile)).all()
        return [self._model_to_entity(model) for model in user_models]
    
    def update(self, user: User) -> None:
        user_model = self.db.query(UserDB).options(joinedload(UserDB.profile)).filter(UserDB.user_id == str(user.user_id)).first()
        if user_model:
            user_model.username = user.username
            user_model.age = user.age
            user_model.email = user.email.value
            if user_model.profile:
                user_model.profile.entorno = user.profile.entorno
                user_model.profile.nivel_educativo = user.profile.nivel_educativo
            self.db.commit()
    
    def delete(self, user_id: uuid.UUID) -> None:
        user_model = self.db.query(UserDB).filter(UserDB.user_id == str(user_id)).first()
        if user_model:
            self.db.delete(user_model)
            self.db.commit()

    def _model_to_entity(self, model: UserDB) -> User:
        password_vo = Password.construct(hashed_value=model.password_hash)
        
        profile_entity = Profile(
            profile_id=uuid.UUID(model.profile.profile_id),
            user_id=uuid.UUID(model.user_id),
            rol=model.profile.rol,
            entorno=model.profile.entorno,
            nivel_educativo=model.profile.nivel_educativo
        )
        
        user_entity = User(
            user_id=uuid.UUID(model.user_id),
            username=model.username,
            age=model.age,
            email=Email(value=model.email),
            password=password_vo,
            profile=profile_entity,
            created_at=model.created_at
        )
        return user_entity

    def _map_entity_to_db_model(self, user: User) -> UserDB:
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