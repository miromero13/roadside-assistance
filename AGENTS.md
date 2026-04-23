# AGENTS.md

## Scope and Structure
- Monorepo with 3 independent apps: `backend/` (FastAPI), `frontend/` (Angular), `mobile/` (Flutter).
- There is no root build/test runner; always run commands inside the target app directory.

## Team Conventions (Project-Specific)
- Domain language is Spanish. Use Spanish entity and field names (`Usuario`, `nombre`, `rol`, etc.).
- Use a single SQLAlchemy `Base` from `backend/app/core/database.py`; do not define additional `Base` classes in model files.

## Backend (`backend/`)
- Start here for API work: `backend/main.py`, `backend/app/routes/`, `backend/app/services/`, `backend/app/models/`.
- Run:
  - `pip install -r requirements.txt`
  - `uvicorn main:app --reload`
- Required env vars (`backend/.env.example`): `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALGORITHM`.
- Current schema behavior: tables are created at startup via `Base.metadata.create_all(bind=engine)` in `backend/main.py`.
- Alembic exists (`backend/alembic.ini`, `backend/alembic/env.py`) but:
  - `alembic.ini` still has placeholder URL (`driver://user:pass@localhost/dbname`)
  - no `alembic/versions/` revisions currently
  - if you rely on autogenerate, ensure models are imported in Alembic context.
- Important gotcha: domain model is `Usuario` (not `User`). Prefer direct imports from domain modules in `app/models/*.py`; `app/models/user.py` is a compatibility re-export layer.
- API prefix is `/api` (routers registered in `backend/main.py`).
- Current RBAC baseline: `auth/register` only creates `conductor`; only `admin` can create talleres/categorías, and only `taller` can create mecánicos for its own taller.
- Current auth baseline: `auth/logout` is available and revokes current JWT in-memory until token expiration (revocation is not persisted across server restarts).
- Current ownership baseline: conductores only manage their own `vehiculos` and can only create averías linked to their own vehicles; admin can read all.
- Current profile baseline: users can read and update their own profile via `/api/users/me` (`GET`/`PUT`), including optional password change with current-password validation.
- Current order baseline: conductor selects taller manually (`/api/talleres/candidatos` + `/api/ordenes`); a single avería cannot have more than one active orden at the same time.
- Current order fallback baseline: when a taller rejects a pending order, the system auto-creates a new pending order for another compatible candidate (same category + coverage), excluding already attempted talleres for that avería.
- Current dispatch baseline: only the order's `taller` can accept/reject and assign mechanics; reassignment cancels previous assignment; mechanic can update only their own assignment states.
- Current order controls baseline: orders expose cancel/manual-complete operations plus history (`historial-estados`) and assignment listing (`asignaciones`) endpoints with role/ownership checks.
- Current budget baseline: only order's `taller` can create presupuestos; only order's conductor can approve/reject; a single orden can have only one `aprobado`, and no new versions can be created after approval.
- Current payment baseline: only order's conductor can create a single pago per orden with exact approved-budget amount; confirming pago creates 10% plataforma commission and auto-completes the orden.
- Current invoice baseline: factura JSON can be generated from a completed pago, with a single factura per pago.
- Current notification baseline: internal `notificaciones` are generated for key order/dispatch/budget/payment events and can be marked read by each user.
- Current rating baseline: only the order's conductor can rate a completed order once; rating updates taller average and notifies taller.
- Current chat baseline: order chat is available from accepted state onward; only order participants (conductor, order taller, active assigned mechanic, admin) can read/send messages.
- Current chat baseline: chat also supports unread count and mark-all-read operations per participant (`/api/chats/{chat_id}/no-leidos/count`, `/api/chats/{chat_id}/leer-todo`).
- Current operations baseline: admin can list pagos/comisiones with filters; taller/admin can update mechanic availability; taller details are public-read and owner/admin editable.
- Current finance admin baseline: admin can list pagos/comisiones/facturas with filters (including date ranges) for operations visibility.
- Current commission baseline: talleres can list/pay their own commissions via `/api/comisiones/mias` and `/api/comisiones/{comision_id}/pagar`; admin keeps global listing via `/api/comisiones/`.
- Current metrics/availability baseline: admin can recalculate/list service metrics; taller/admin can manage taller horarios/bloqueos; users can register and deactivate push devices.
- Current metrics/availability baseline: admin can recalculate/list service metrics with date/rating filters; metrics auto-refresh when an order is completed (payment or manual completion).
- Current catalog baseline: categories are listable and admin-editable; taller/admin can create/list/update/soft-disable `servicios_taller` for each taller.
- Current catalog baseline: category listing endpoint is `/api/categorias-servicio` (not `/api/categorias`).
- Seed baseline: `backend/scripts/seed_mvp.py` is idempotent and now seeds a broad dataset (multi-role users, 3 talleres, 6 mecánicos, categorías/servicios, vehículos/averías, órdenes in multiple states, presupuestos/pagos/comisiones/facturas, chat/notificaciones, disponibilidad, push, métricas).
- Seed baseline: fixed credentials include `admin@aci.com`, `conductor@aci.com`, `taller@aci.com`, `mecanico@aci.com` and extra demo accounts (`conductor2/3`, `taller2/3`, `mecanico2..6`) all with known passwords in the seed script.
- API testing baseline: Postman collection `backend/postman/mvp_e2e.postman_collection.json` was expanded to cover current endpoints and dynamic variable capture (tokens/IDs) across modules.

## Frontend (`frontend/`)
- Run:
  - `npm install`
  - `npm run start`
  - `npm run build`
  - `npm run test`
- Tooling: Angular 21 + Spartan/Helm + Tailwind v4 (`frontend/src/styles.css`).
- Entrypoints:
  - bootstrap: `frontend/src/main.ts`
  - root component: `frontend/src/app/app.ts`
  - routes: `frontend/src/app/app.routes.ts` (currently empty).
- No `src/**/*.spec.ts` files currently, even though test script exists.

## Mobile (`mobile/`)
- Use FVM commands (project expects FVM):
  - `fvm flutter pub get`
  - `fvm flutter run`
  - `fvm flutter test`
- Flutter channel pinned via `mobile/.fvmrc` (`stable`).
- App is mostly Flutter scaffold (`mobile/lib/main.dart`) with default widget test.

## Verification Strategy
- Validate only the app you changed (backend/frontend/mobile), since there is no unified monorepo pipeline.
- For backend changes, at minimum verify server startup and impacted endpoints.
- Backend seed command available: `py scripts/seed_mvp.py`.
- Backend smoke command available: `py scripts/smoke_e2e.py` (starts local uvicorn on port 8001 and validates the MVP end-to-end flow).
- For frontend changes, at minimum verify `npm run build`.
- For mobile changes, at minimum verify `fvm flutter test` or `fvm flutter run` if UI behavior changed.

## AGENTS.md Maintenance
- Update `AGENTS.md` whenever repository changes could cause an agent to make wrong assumptions.
- Always update it when changing folder structure, run/verification commands, naming conventions, migration flow, or CI/lint/test tooling.
- If you discover missing high-signal context during a task, add a short, verifiable note in the same task.
- Keep it compact and repo-specific; avoid generic advice.

## Repo Reality Checks
- No CI workflows found under `.github/workflows/`.
- No pre-commit config found.
- No existing agent instruction files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.cursor/rules`, `.github/copilot-instructions.md`, `opencode.json`).
