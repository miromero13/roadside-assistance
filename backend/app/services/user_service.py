from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID

from app.auth.hash import hash_password
from app.auth.hash import verify_password
from app.models.usuario import Usuario
from app.schemas.user_schema import UsuarioActualizarPerfil, UsuarioActualizarRol, UsuarioCrear


def create_user(db: Session, user: UsuarioCrear) -> Usuario:
    password_hash = hash_password(user.password)

    db_user = Usuario(
        nombre=user.nombre,
        apellido=user.apellido,
        email=user.email,
        telefono=user.telefono,
        password_hash=password_hash,
        rol=user.rol,
    )
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("El correo ya está registrado")


def get_user(db: Session, user_id: UUID) -> Usuario | None:
    result = db.execute(select(Usuario).where(Usuario.id == user_id))
    return result.scalars().first()


def get_users(db: Session, skip: int = 0, limit: int = 10):
    result = db.execute(select(Usuario).offset(skip).limit(limit))
    return result.scalars().all()


def get_users_count(db: Session):
    result = db.execute(select(func.count(Usuario.id)))
    return result.scalar_one()


def update_user_rol(
    db: Session, user_id: UUID, update_data: UsuarioActualizarRol
) -> Usuario | None:
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        return None

    user.rol = update_data.rol
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(
    db: Session,
    user: Usuario,
    payload: UsuarioActualizarPerfil,
) -> Usuario:
    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        raise ValueError("No se enviaron campos para actualizar")

    password_actual = changes.pop("password_actual", None)
    password_nueva = changes.pop("password_nueva", None)

    if password_actual is not None or password_nueva is not None:
        if not password_actual or not password_nueva:
            raise ValueError("Para cambiar contraseña debes enviar password_actual y password_nueva")
        if not verify_password(password_actual, user.password_hash):
            raise ValueError("La contraseña actual es incorrecta")
        user.password_hash = hash_password(password_nueva)

    for field, value in changes.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# Alias de compatibilidad temporal
update_user_type = update_user_rol
