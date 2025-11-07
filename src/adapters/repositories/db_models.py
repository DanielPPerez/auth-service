# src/adapters/repositories/db_models.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
import uuid
import datetime

from .database import Base
from src.domain.value_objects.enums import Rol, Entorno, NivelEducativo

class UserDB(Base):
    __tablename__ = "users"
    user_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relación uno a uno con el perfil
    profile = relationship("ProfileDB", back_populates="user", uselist=False, cascade="all, delete-orphan")

class ProfileDB(Base):
    __tablename__ = "profiles"
    profile_id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.user_id"), nullable=False)
    rol = Column(SQLAlchemyEnum(Rol), default=Rol.ALUMNO)
    entorno = Column(SQLAlchemyEnum(Entorno), nullable=False)
    nivel_educativo = Column(SQLAlchemyEnum(NivelEducativo), nullable=False)
    
    user = relationship("UserDB", back_populates="profile")