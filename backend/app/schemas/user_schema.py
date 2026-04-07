from pydantic import BaseModel, EmailStr
from typing import List
from uuid import UUID
from app.schemas.enums import UserTypeEnum, GenderEnum

#  Para registro
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    gender: GenderEnum
    user_type: UserTypeEnum

#  Para login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

#  Para leer usuario en respuestas (registro, perfil)
class UserOut(BaseModel):
    id: UUID 
    name: str
    email: EmailStr
    gender: GenderEnum
    user_type: UserTypeEnum


    class Config:
        from_attributes = True

#  Para paginación de usuarios (si aplicas en /users)
class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    gender: GenderEnum
    user_type: UserTypeEnum

    model_config = {
        "from_attributes": True
    }

class UsersPaginatedResponse(BaseModel):
    data: List[UserRead]
    countData: int
    
class UserUpdateType(BaseModel):
    user_type: UserTypeEnum
