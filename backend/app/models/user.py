from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from app.schemas.enums import UserTypeEnum, GenderEnum
from app.core.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    gender = Column(SQLAlchemyEnum(GenderEnum), nullable=False)
    user_type = Column(SQLAlchemyEnum(UserTypeEnum), nullable=False)
