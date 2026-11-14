# GEMINI.md — Guía de referencia del repositorio
- Idioma: Respondé siempre en español (incluyendo planes de implementación, explicaciones, resúmenes de cambios y comentarios en el código).

Este documento resume la arquitectura, el stack tecnológico, los comandos de ejecución y las convenciones de **Educar para Transformar** (Sistema de Gestión Escolar: API REST en FastAPI + interfaz web/multiplataforma en Flet sobre PostgreSQL).

---

## 1. Stack tecnológico y dependencias

La gestión de dependencias se realiza exclusivamente con **`uv`** (`pyproject.toml` y `uv.lock`).

> **Nota:** `requirements.txt` contiene marcadores de conflicto de Git sin resolver (`<<<<<<< HEAD` / `>>>>>>> origin/main`); no usarlo como fuente de verdad.

- **Python:** `3.12` (`.python-version` define `3.12`; CI y Sonar usan `3.12`).
- **Backend / API:**
  - `fastapi>=0.141.1` + `uvicorn[standard]>=0.52.4`
  - `sqlalchemy>=2.0.54` + `psycopg2-binary>=2.9.13` (PostgreSQL 14+ / CI usa Postgres 16)
  - `pydantic-settings>=2.15.0` (Pydantic v2)
  - `pyjwt>=2.15.1` + `bcrypt>=5.0.0` + `passlib[bcrypt]>=1.7.4`
  - `apscheduler>=3.11.3` (`AsyncIOScheduler` para tareas programadas)
  - `openpyxl>=3.1.5` (exportación de reportes `.xlsx`)
  - `fpdf2>=2.8.9` (`from fpdf import FPDF` para generación de facturas en PDF)
  - `python-dotenv>=1.2.3`, `python-multipart>=0.0.32`
- **Frontend / UI:**
  - `flet>=0.86.5` (servido dentro de FastAPI vía `flet.fastapi.app(...)` o standalone)
  - `httpx>=0.28.1` (cliente HTTP asíncrono en `frontend/app/api_client.py`)
- **Calidad y testing (`[dependency-groups].dev`):**
  - `pytest>=9.1.1`, `pytest-asyncio>=1.4.0`, `pytest-cov>=7.1.0`
  - `ruff>=0.16.10` (configurado también en `.pre-commit-config.yaml`)
  - `flet-cli`, `flet-desktop`, `flet-web`, `flet[test]`

---

## 2. Estructura del repositorio

```text
FrontEducar/
├── backend/
│   ├── app/
│   │   ├── main.py                # Instancia FastAPI, create_all, lifespan, CORS, routers y montaje Flet en "/"
│   │   ├── api/
│   │   │   ├── deps.py            # Dependencias JWT: get_current_user, require_roles(*roles)
│   │   │   └── v1/
│   │   │       ├── api.py         # Router agregador /api/v1
│   │   │       └── endpoints/     # academico, auth, comunidad, dashboard, evaluacion, finanzas, personas, reportes, servicios
│   │   ├── core/
│   │   │   ├── database.py        # DATABASE_URL, engine, SessionLocal, Base, get_db
│   │   │   └── scheduler.py       # Tareas mensuales APScheduler (cierre mensual y aviso a morosos)
│   │   ├── models/                # Modelos SQLAlchemy ORM (academico, comunidad, evaluacion, finanzas, personas, seguridad, servicios)
│   │   ├── repositories/          # CRUDBase genérico (base.py) y repositorios por dominio
│   │   ├── schemas/               # Esquemas Pydantic v2 (Create, Update, Response)
│   │   └── services/              # Lógica de negocio (singletons) + email_service.py y pdf_generator.py
│   └── unificar.py                # Script utilitario (no runtime) para volcar código a texto
├── frontend/
│   ├── run.py                     # Entrypoint unificado recomendado (API + Flet en puerto 8000)
│   ├── main.py                    # Entrypoint Flet standalone (requiere backend corriendo aparte)
│   ├── unificar.py                # Script utilitario (no runtime)
│   └── app/
│       ├── main_view.py           # Router Flet, guardias de sesión/rol y mapeo de rutas
│       ├── api_client.py          # Cliente HTTP asíncrono singleton (APIClient)
│       ├── assets/                # Imágenes de app (icon.png, splash_android.png)
│       ├── components/            # constants.py, admin_layout.py, portal_layout.py, navbar.py, sidebar.py, topbar.py, footer.py, form_controls.py, table_view.py, password_dialog.py
│       └── pages/                 # Vistas: públicas, admin_*, padre_*, docente_*, alumno_*
├── mobile/                        # 📱 APLICACIÓN MÓVIL DEDICADA (PARTE 3 - Flet)
│   ├── main.py                    # Entrypoint Flet móvil nativo (BottomNavigationBar)
│   ├── api_client.py              # Cliente HTTP móvil asíncrono singleton (MobileAPIClient)
│   ├── assets/                    # Íconos y splash screen móvil
│   ├── components/                # constants.py, mobile_scaffold.py (TopBar + BottomNavigationBar)
│   └── pages/                     # login_page.py, home_page.py, facturas_page.py, servicios_page.py, perfil_page.py
├── tests/
│   ├── backend/                   # conftest.py (PostgreSQL educar_test) + tests de API/unitarios
│   └── frontend/                  # test_ui_deportes.py
├── app/                           # Resto inicial de Flet (legado; la app activa vive en backend/ + frontend/)
├── scripts/metrics.py             # Métricas DORA vía GitHub API (GITHUB_TOKEN)
├── Creacion_tablas.pgsql          # DDL completo de PostgreSQL (incluye tablas de finanzas)
├── Insercion_datosDB.pgsql        # Datos semilla de desarrollo
├── CREATE DATABASE educar_db;.pgsql
├── fix_auth.py                    # Script para restablecer password de admin_gral a "password123"
├── pyproject.toml                 # Configuración de proyecto, uv, pytest, ruff y build
├── sonar-project.properties       # Configuración de SonarCloud
└── .github/workflows/ci.yml       # Pipeline CI (Lint con Ruff + Build & Test con Postgres 16 + Sonar)
```

---

## 3. Reglas de arquitectura

### Backend (`backend/app`)
1. **Arquitectura en capas estricta:**
   `Endpoint (api/v1/endpoints)` → `Service (services/)` → `Repository (repositories/)` → `Model (models/)`
   - **Endpoints:** solo declaran rutas, validan schemas Pydantic, aplican seguridad (`Depends(get_current_user)` o `Depends(require_roles(...))`), inyectan `db: Session = Depends(get_db)` y delegan al servicio singleton correspondiente.
   - **Services:** contienen toda la lógica de negocio, validaciones referenciales, control de duplicados, captura de `IntegrityError` (con `db.rollback()` y `HTTPException(409)`), y `db.commit()`. Se exportan como instancias singleton (ej. `seguridad_service`, `academico_service`, `personas_service`, `servicios_escolares_service`, `comunidad_service`, `evaluacion_service`, `finanzas_service`).
   - **Repositories:** heredan de `CRUDBase[Model, CreateSchema, UpdateSchema]` en `backend/app/repositories/base.py`. Las consultas custom deben usar SQLAlchemy 2.0 (`select(...).where(...)` con `db.scalars(stmt)`). *(Nota: `finanzas` aún consulta `db.query(...)` directamente en servicio/endpoint; al ampliarlo, migrar o mantener consistencia hacia repositorios).*
   - **Models y Schemas:** todo modelo nuevo debe importarse en `backend/app/models/__init__.py` para quedar registrado en `Base.metadata`.

2. **Orden de montaje en `backend/app/main.py`:**
   - Todos los routers REST deben registrarse bajo `/api/v1` **antes** de `app.mount("/", flet_fastapi.app(flet_main))`. Flet es un catch-all en `/` y taparía cualquier ruta montada después.

3. **Autenticación, RBAC y aislamiento por rol:**
   - Roles válidos en BD (`tabla rol`): `ADMIN`, `TEACHER`, `PARENT`, `STUDENT`.
   - Todo endpoint privado exige JWT Bearer vía `get_current_user` o `require_roles(...)`.
   - **Excepción:** los endpoints de descarga Excel en `backend/app/api/v1/endpoints/reportes.py` aceptan `?token=<jwt>` mediante `_autorizar_admin(db, token)` porque se abren directamente en el navegador.
   - Endpoints públicos sin autenticación: `/api/v1/health`, `POST /api/v1/auth/login`, y envíos/consultas públicas en `comunidad` (solicitud de inscripción, contacto, postulación laboral, envío de opinión y listado de opiniones aprobadas).
   - Endpoints consultados por alumnos o tutores (`personas`, `evaluacion`, `servicios`, `finanzas`) deben restringir el acceso a los legajos propios (`current_user.legajo_alumno`) o de sus hijos vinculados en `padre_alumno`.

### Frontend (`frontend/app`)
1. **Desacoplamiento total del backend:**
   - El frontend **nunca** importa modelos, repositorios ni `SessionLocal` de `backend`. Toda comunicación HTTP pasa por el singleton `api_client` en `frontend/app/api_client.py`.
2. **Estado de sesión y navegación (`frontend/app/main_view.py`):**
   - La sesión se guarda en atributos de `ft.Page`: `page.auth_token`, `page.auth_rol`, `page.auth_user`, sincronizados con `api_client.set_token(...)` / `api_client.clear_token()`.
   - Las rutas `/admin/*` y `/portal/*` están protegidas por guardias en `route_change` según `SECCION_POR_ROL` y `RUTA_INICIAL_POR_ROL`.
3. **Convención de vistas y layouts:**
   - **Páginas públicas** (`home`, `login`, `contacto`, `inscripciones`, `niveles`, `noticias`, `opiniones`, `empleo`, `bienestar_estudiantil`, `quienes_somos`): devuelven `list[ft.Control]` y `main_view.py` las envuelve con `create_navbar` y `create_footer`.
   - **Páginas internas** (`admin_*`, `padre_*`, `docente_*`, `alumno_*`): funciones `async def get_<modulo>_view(page: ft.Page)` que retornan `admin_layout(...)` (`ft.Row`) o `portal_layout(...)` (`ft.Container`).
   - Usar **siempre** `frontend.app.components.portal_layout.portal_layout` (no `frontend/app/pages/portal_layout.py`, que es un remanente legado).
   - Reutilizar los tokens de diseño de `frontend/app/components/constants.py` (`TEAL`, `TEAL_DARK`, `TEAL_LIGHT`, `ORANGE`, `BG_PAGE`, `BORDER_COLOR`, alturas y radios) y los helpers de `form_controls.py` y `table_view.py`.

---

## 4. Comandos de ejecución, pruebas y calidad

### Configuración inicial
```bash
uv sync --dev              # Instala dependencias de runtime y desarrollo
cp .env.example .env       # Ajustar DATABASE_URL y SECRET_KEY
```

Variables de entorno relevantes:
- Obligatorias: `DATABASE_URL` (ej. `postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/educar_db`), `SECRET_KEY`.
- Opcionales: `ACCESS_TOKEN_EXPIRE_MINUTES` (default `1440`), `API_BASE_URL` (default `http://127.0.0.1:8000/api/v1`), `TEST_DATABASE_URL` (default `postgresql+psycopg2://postgres@127.0.0.1:5432/educar_test`), `EMAIL_SENDER`, `EMAIL_PASSWORD`.

### Base de datos PostgreSQL
```bash
createdb educar_db
psql -d educar_db -f "Creacion_tablas.pgsql"
psql -d educar_db -f "Insercion_datosDB.pgsql"
```
*(Si se usa un cluster local en `.pgdata/`: iniciar antes con `pg_ctl -D .pgdata -l .pgdata/server.log start`).*

### Ejecución local
- **Aplicación completa (API FastAPI + Web Flet en el mismo proceso):**
  ```bash
  uv run python frontend/run.py
  ```
  - Interfaz web: `http://127.0.0.1:8000/`
  - Documentación Swagger: `http://127.0.0.1:8000/docs`
  - Healthcheck: `http://127.0.0.1:8000/api/v1/health`
- **Solo cliente Flet Web (requiere el backend activo aparte):**
  ```bash
  uv run flet run
  ```
- **📱 Aplicación Móvil Dedicada (para app Flet de Android o emulador):**
  ```bash
  uv run flet run mobile/main.py
  # O en un puerto específico para abrir desde el celular por Wi-Fi:
  uv run flet run mobile/main.py --port 8550
  ```
- **Restablecer clave de `admin_gral` (`password123`):**
  ```bash
  uv run python fix_auth.py
  ```

### Tests y cobertura
```bash
# Suite completa (requiere PostgreSQL activo; crea/resetea la BD educar_test)
uv run pytest

# Mismo comando de cobertura exigido en CI (mínimo 50%)
uv run pytest --cov=backend --cov-report=term-missing --cov-report=xml --cov-fail-under=50

# Tests unitarios/UI sin dependencia de PostgreSQL
uv run pytest tests/backend/test_scheduler.py tests/backend/test_main.py tests/frontend/test_ui_deportes.py
```
> **Nota sobre `pytest`:** `pyproject.toml` define `testpaths = ["backend/tests"]` (ruta inexistente), por lo que `pytest` emite un `PytestConfigWarning` y busca recursivamente en `tests/`. Al agregar tests, ubicarlos en `tests/backend/` o `tests/frontend/`.

### Linting, formato y verificación de sintaxis
```bash
uv run ruff check .               # Verificar reglas de lint
uv run ruff check --fix .         # Corregir errores auto-reparables (ej. orden de imports)
uv run ruff format .              # Formatear código
uv run python -m compileall -q .  # Verificación de sintaxis usada en CI
```

### Build (empaquetado Flet)
```bash
uv run flet build web -v          # También soporta apk, ipa, linux, windows
```

---

## 5. Convenciones de código

- **Idioma:** Todo el dominio, nombres de tablas/columnas, variables de negocio, docstrings, comentarios y mensajes de respuesta HTTP se escriben en **español**. Única excepción estándar: los códigos de rol (`ADMIN`, `TEACHER`, `PARENT`, `STUDENT`) y prefijos HTTP/JWT.
- **Imports:** Siempre absolutos desde la raíz del repositorio (`from backend.app...`, `from frontend.app...`) y ordenados según Ruff (`I001`).
- **Tipado:** Usar sintaxis de Python 3.10+/3.12 (`int | None`, `list[...]`, `dict[...]`).
- **Reglas de Ruff:** Respetar la configuración `[tool.ruff.lint]` en `pyproject.toml` (no introducir código con errores fuera de la lista `ignore`, especialmente `F821` e `I001`).
- **Claves primarias y bajas en BD:**
  - `alumno.legajo` y `profesor.legajo` son enteros no autoincrementales; `PersonasService.create_alumno` autogenera `(max_legajo or 999) + 1`.
  - Alumnos y profesores usan baja lógica (`soft_delete` pasando `estado_alumno`/`estado` a `"INACTIVO"`).
  - Si se insertan registros semilla con IDs explícitos en PostgreSQL, actualizar las secuencias con `setval(pg_get_serial_sequence(...))`.
- **Pendientes / puntos de atención conocidos en el estado actual del repo:**
  - `backend/app/core/scheduler.py` referencia `Factura`, `Alumno`, `ItemFactura`, `generar_pdf_factura` y `enviar_correo_con_pdf` sin importarlos (genera errores `F821` en `ruff check`).
  - `backend/app/api/v1/endpoints/finanzas.py`, `frontend/app/pages/padre_dashboard.py` y `frontend/app/pages/padre_facturas.py` tienen imports desordenados (`I001` en `ruff check`).
  - Existen archivos legados que no deben confundirse con los módulos activos: `app/` en la raíz y `frontend/app/pages/portal_layout.py`.
