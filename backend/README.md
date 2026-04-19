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
- `GET /api/users/me`
- `GET /api/users/{user_id}`
- `GET /api/users/`
- `PATCH /api/users/{user_id}/rol`
- `POST /api/users/`
- `POST /api/gestion/talleres`
- `POST /api/gestion/mecanicos`
- `POST /api/gestion/categorias-servicio`
- `POST /api/vehiculos`
- `GET /api/vehiculos`
- `GET /api/vehiculos/{vehiculo_id}`
- `PUT /api/vehiculos/{vehiculo_id}`
- `DELETE /api/vehiculos/{vehiculo_id}`
- `POST /api/averias`
- `GET /api/averias`
- `GET /api/averias/{averia_id}`
- `POST /api/averias/{averia_id}/medios`
- `GET /api/talleres/candidatos`
- `POST /api/ordenes`
- `GET /api/ordenes`
- `GET /api/ordenes/{orden_id}`
- `PUT /api/ordenes/{orden_id}/aceptar`
- `PUT /api/ordenes/{orden_id}/rechazar`
- `POST /api/ordenes/{orden_id}/asignar-mecanico`
- `PUT /api/asignaciones/{asignacion_id}/estado`
- `POST /api/ordenes/{orden_id}/presupuestos`
- `GET /api/ordenes/{orden_id}/presupuestos`
- `PUT /api/presupuestos/{presupuesto_id}/aprobar`
- `PUT /api/presupuestos/{presupuesto_id}/rechazar`
- `POST /api/pagos`
- `GET /api/pagos/{pago_id}`
- `POST /api/pagos/{pago_id}/confirmar`
- `GET /api/notificaciones`
- `PUT /api/notificaciones/leer-todas`
- `PUT /api/notificaciones/{notificacion_id}/leer`
- `POST /api/ordenes/{orden_id}/calificaciones`
- `GET /api/ordenes/{orden_id}/calificaciones`
- `POST /api/pagos/{pago_id}/factura`
- `GET /api/facturas`
- `GET /api/facturas/{factura_id}`
- `GET /api/ordenes/{orden_id}/factura`
- `GET /api/ordenes/{orden_id}/chat`
- `GET /api/chats/{chat_id}/mensajes`
- `POST /api/chats/{chat_id}/mensajes`
- `PUT /api/chats/{chat_id}/mensajes/{mensaje_id}/leer`
- `PUT /api/chats/{chat_id}/leer-todo`
- `GET /api/chats/{chat_id}/no-leidos/count`
- `PATCH /api/mecanicos/{mecanico_id}/disponibilidad`
- `GET /api/talleres/{taller_id}`
- `PATCH /api/talleres/{taller_id}`
- `GET /api/pagos`
- `GET /api/comisiones`
- `POST /api/metricas/ordenes/{orden_id}/recalcular`
- `GET /api/metricas/ordenes`
- `PUT /api/ordenes/{orden_id}/cancelar`
- `PUT /api/ordenes/{orden_id}/completar`
- `GET /api/ordenes/{orden_id}/historial-estados`
- `GET /api/ordenes/{orden_id}/asignaciones`
- `GET /api/talleres/{taller_id}/horarios`
- `POST /api/talleres/{taller_id}/horarios`
- `PATCH /api/talleres/{taller_id}/horarios/{horario_id}`
- `DELETE /api/talleres/{taller_id}/horarios/{horario_id}`
- `GET /api/talleres/{taller_id}/bloqueos`
- `POST /api/talleres/{taller_id}/bloqueos`
- `DELETE /api/talleres/{taller_id}/bloqueos/{bloqueo_id}`
- `POST /api/push/dispositivos`
- `GET /api/push/dispositivos`
- `DELETE /api/push/dispositivos/{dispositivo_id}`
- `GET /api/categorias-servicio`
- `PATCH /api/categorias-servicio/{categoria_id}`
- `POST /api/talleres/{taller_id}/servicios`
- `GET /api/talleres/{taller_id}/servicios`
- `PATCH /api/servicios-taller/{servicio_id}`
- `DELETE /api/servicios-taller/{servicio_id}`

### Autenticación

- El login y el registro devuelven un token JWT tipo Bearer.
- `POST /api/auth/register` crea únicamente usuarios con rol `conductor`.
- Las rutas protegidas usan `Authorization: Bearer <token>`.
- El usuario actual se resuelve desde el token en `app/auth/dependencies.py`.

### Reglas de acceso actuales

- Solo `admin` puede crear talleres y categorías de servicio.
- Solo `taller` puede crear mecánicos asociados a su propio taller.
- Las operaciones globales de usuarios (`GET /api/users`, `PATCH /api/users/{user_id}/rol`, `POST /api/users/`) requieren rol `admin`.
- Solo `conductor` puede crear/listar sus vehículos y crear averías sobre vehículos propios.
- `admin` puede consultar cualquier vehículo o avería, pero no crear averías en nombre de conductores.
- No se puede eliminar un vehículo si tiene averías registradas.
- La selección de taller es manual por conductor con `GET /api/talleres/candidatos` y `POST /api/ordenes`.
- No se permite crear una nueva orden si la avería ya tiene una orden activa.
- Solo el taller dueño puede aceptar/rechazar/asignar mecánicos a su orden.
- En reasignación, la asignación anterior se marca como `cancelado` y se crea una nueva.
- Solo el mecánico asignado puede actualizar su estado operativo.
- No se permite pasar una asignación a `atendiendo` sin presupuesto aprobado para la orden.
- Solo el taller dueño de la orden puede crear presupuestos versionados.
- Solo el conductor dueño puede aprobar o rechazar presupuestos.
- Solo puede existir un presupuesto `aprobado` por orden; al aprobar uno, los demás `enviado` pasan a `vencido`.
- Si una orden ya tiene un presupuesto aprobado, no se permite crear nuevas versiones.
- Solo puede existir un pago por orden.
- El monto del pago debe ser exactamente el monto total del presupuesto aprobado.
- Un pago completado genera comisión de plataforma del 10% y completa automáticamente la orden.
- Las notificaciones internas se generan automáticamente en eventos de orden, asignación, presupuesto y pago.
- Solo el conductor dueño puede calificar una orden completada, con una única calificación por orden.
- La calificación actualiza el promedio del taller y genera notificación interna al taller.
- La factura se genera en formato JSON para pagos completados y solo permite una factura por pago.
- El chat operativo se habilita desde que la orden está aceptada y permite comunicación entre conductor, taller y mecánico asignado.
- El chat permite marcar todo como leído y consultar el conteo de no leídos por usuario participante.
- Taller y admin pueden actualizar disponibilidad del mecánico; solo taller dueño o admin pueden actualizar datos del taller.
- `GET /api/pagos`, `GET /api/comisiones` y `GET /api/facturas` son listados administrativos con filtros.
- `GET /api/ordenes` ahora acepta filtro opcional por estado.
- `GET /api/metricas/ordenes` permite filtros por fecha de creación y rango de calificación final.
- Las métricas de servicio se recalculan automáticamente al completar la orden por pago confirmado o cierre manual.
- `GET /api/metricas/ordenes` y el recálculo de métricas son operaciones administrativas.
- Horarios y bloqueos del taller son gestionables por admin o por el taller dueño.
- El registro de dispositivos push queda habilitado para cada usuario autenticado.
- El catálogo de servicios permite listar/actualizar categorías (admin) y gestionar servicios por taller (dueño/admin) con desactivación lógica.
- La orden puede cancelarse por participante autorizado y tiene endpoints de historial y asignaciones para trazabilidad operativa.

## Modelo principal

El modelo principal actual es `Usuario`, definido en `app/models/usuario.py`.

Los modelos están separados por dominio dentro de `app/models/` (por ejemplo: `usuario.py`, `taller.py`, `averia.py`, `orden.py`, `finanzas.py`, `comunicacion.py`).

Todos los modelos deben usar el `Base` único definido en `app/core/database.py`.

`app/models/user.py` se mantiene solo como capa de compatibilidad de imports.

Campos principales de `Usuario`:

- `id`: UUID
- `nombre`: nombre
- `apellido`: apellido
- `email`: correo único
- `telefono`: teléfono
- `password_hash`: contraseña encriptada
- `rol`: enum de rol
- `activo`: estado del usuario

## Esquemas importantes

Los esquemas Pydantic están en `app/schemas/user_schema.py`:

- `UsuarioCrear`: registro de usuario
- `UsuarioLogin`: inicio de sesión
- `UsuarioRead`: respuesta pública de usuario
- `UsuariosPaginadosResponse`: listado con conteo
- `UsuarioActualizarRol`: actualización del rol de usuario

## Notas de desarrollo

- La app crea las tablas al arrancar con `Base.metadata.create_all(bind=engine)`.
- También existe `app/core/create_tables.py`, que permite crear las tablas de forma manual ejecutando ese script.
- Alembic está configurado, pero en este momento no hay migraciones generadas en `alembic/versions`, así que el flujo actual de tablas es automático por arranque o manual con `create_tables.py`.
- Si vas a empezar a usar migraciones, revisa la configuración de `sqlalchemy.url` en `alembic.ini` o en el entorno de ejecución.
- Las respuestas están unificadas con un helper en `app/utils/response.py`.
