# Backend

Backend del proyecto Roadside Assistance construido con FastAPI, SQLAlchemy y PostgreSQL.

## Requisitos

- Python 3.10 o superior
- PostgreSQL
- `pip`
- Un entorno virtual recomendado (`venv`)

## Clonar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd roadside-assistance/backend
```

Si ya tienes el repositorio descargado, entra directamente a la carpeta `backend`.

## Configuración

1. Crea y activa un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Crea el archivo `.env` en la raíz de `backend` usando `.env.example` como base:

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_base_datos
SECRET_KEY=tu_clave_secreta
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
```

4. Asegúrate de que la base de datos exista antes de iniciar la app.

## Ejecutar el proyecto

```bash
uvicorn main:app --reload
```

La API queda disponible normalmente en `http://127.0.0.1:8000`.

FastAPI también expone documentación automática en:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Estructura del backend

```text
backend/
├── main.py
├── requirements.txt
├── alembic.ini
├── .env.example
├── alembic/
└── app/
    ├── auth/
    ├── core/
    ├── models/
    ├── routes/
    ├── schemas/
    ├── services/
    └── utils/
```

### Qué hace cada carpeta

- `app/auth`: autenticación, JWT, hash de contraseñas y dependencias de seguridad.
- `app/core`: configuración general, conexión a base de datos y manejo de errores.
- `app/models`: modelos de SQLAlchemy.
- `app/routes`: rutas HTTP del sistema.
- `app/schemas`: esquemas Pydantic y enums para validación.
- `app/services`: lógica de negocio y acceso a datos.
- `app/utils`: utilidades compartidas, como el formato estándar de respuestas.
- `alembic`: migraciones de base de datos.

## Flujo de rutas

El archivo `main.py` registra los routers con el prefijo `/api`, por lo que las rutas públicas quedan agrupadas así:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/users/`
- `GET /api/users/me`
- `GET /api/users/{user_id}`
- `GET /api/users/`
- `PATCH /api/users/{user_id}/type`

### Autenticación

- El login y el registro devuelven un token JWT tipo Bearer.
- Las rutas protegidas usan `Authorization: Bearer <token>`.
- El usuario actual se resuelve desde el token en `app/auth/dependencies.py`.

## Modelo principal

El modelo principal actual es `User`, ubicado en `app/models/user.py`.

Todos los modelos deben heredar de `app/core/base_model.py`, donde está el modelo base compartido.

Campos principales:

- `id`: UUID
- `created_at`: fecha de creación automática
- `updated_at`: fecha de actualización automática
- `name`: nombre del usuario
- `email`: correo único
- `hashed_password`: contraseña encriptada
- `gender`: enum de género
- `user_type`: enum de tipo de usuario

## Esquemas importantes

Los esquemas Pydantic están en `app/schemas/user_schema.py`:

- `UserCreate`: registro de usuario
- `UserLogin`: inicio de sesión
- `UserRead` y `UserOut`: respuesta pública de usuario
- `UsersPaginatedResponse`: listado con conteo
- `UserUpdateType`: actualización del tipo de usuario

## Notas de desarrollo

- La app crea las tablas al arrancar con `Base.metadata.create_all(bind=engine)`.
- También existe `app/core/create_tables.py`, que permite crear las tablas de forma manual ejecutando ese script.
- Alembic está configurado, pero en este momento no hay migraciones generadas en `alembic/versions`, así que el flujo actual de tablas es automático por arranque o manual con `create_tables.py`.
- Si vas a empezar a usar migraciones, revisa la configuración de `sqlalchemy.url` en `alembic.ini` o en el entorno de ejecución.
- Las respuestas están unificadas con un helper en `app/utils/response.py`.
