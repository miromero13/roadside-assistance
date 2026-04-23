from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schema import UsuarioCrear, UsuarioLogin, UsuarioRead, UsuarioRegistroConductor
from app.models.enums import UserRole
from app.models.usuario import Usuario
from app.core.database import get_db
from app.auth.hash import verify_password
from app.auth.dependencies import get_current_payload
from app.auth.jwt import create_access_token, revoke_token_payload
from app.services.user_service import create_user


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(usuario: UsuarioRegistroConductor, db: Session = Depends(get_db)):
    nuevo_usuario = UsuarioCrear(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        telefono=usuario.telefono,
        password=usuario.password,
        rol=UserRole.CONDUCTOR,
    )
    try:
        db_user = create_user(db, nuevo_usuario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    access_token = create_access_token(data={"sub": str(db_user.id)})

    user_data = UsuarioRead.model_validate(db_user).model_dump()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@router.post("/login")
def login(user_data: UsuarioLogin, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    usuario_data = UsuarioRead.model_validate(user).model_dump()
    return {"access_token": access_token, "token_type": "bearer", "user": usuario_data}


@router.post("/logout")
def logout(payload_and_token: tuple[dict, str] = Depends(get_current_payload)):
    payload, _ = payload_and_token
    revoke_token_payload(payload)
    return {"message": "Sesión cerrada exitosamente"}
