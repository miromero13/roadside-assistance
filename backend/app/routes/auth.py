from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserRead, UserLogin, UserOut
from app.models.user import User
from app.core.database import get_db
from app.auth.hash import verify_password
from app.auth.jwt import create_access_token
from app.services.user_service import create_user
from app.utils.response import response


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)

    access_token = create_access_token(data={"sub": str(db_user.id)})

    user_data = UserRead.model_validate(db_user).model_dump()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user": user}
