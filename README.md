# Educar para Transformar

Sistema de gestión escolar: **API REST (FastAPI) + interfaz web (Flet) sobre PostgreSQL**.

- `backend/` → API REST (FastAPI + SQLAlchemy): autenticación JWT, personas, académico, servicios escolares.
- `frontend/` → Interfaz (Flet) montada sobre el mismo proceso FastAPI y cliente HTTP (`api_client.py`).
- `Creacion_tablas.pgsql` / `Insercion_datosDB.pgsql` → scripts de esquema y datos de prueba.

## Funcionalidades

- **Seguridad**: login JWT, control de acceso por rol (ADMIN, TEACHER, PARENT, STUDENT), cambio de contraseña y usuarios vinculados a alumnos, docentes o tutores.
- **Gestión académica**: ABM de niveles, cursos, materias, horarios y asignaciones docente-materia-curso.
- **Personas**: ABM de alumnos, docentes y tutores con sus vínculos familiares.
- **Servicios escolares**: deportes (grupos e inscripciones), transporte y comedor.
- **Comunidad**: formularios públicos de inscripción, contacto, opiniones y postulaciones laborales; bandeja de mensajes y moderación de opiniones desde el panel admin.
- **Notas y asistencia**: los docentes cargan calificaciones y planillas de asistencia; alumnos y tutores consultan notas, promedios y presentismo (cada rol ve solo lo que le corresponde).
- **Reportes**: exportación a Excel (.xlsx) de alumnos, cursos-materias, deportes, transporte, solicitudes y resumen general (solo ADMIN).
- **Panel de control**: KPIs y resumen de gestión con datos reales.

## Requisitos

- **Python 3.12.x** (3.13+ no soportado)
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL (14 o superior)

## Puesta en marcha

### 1. Instalar dependencias

```bash
uv sync
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Ajustar `DATABASE_URL` y `SECRET_KEY` en `.env`.

### 3. Crear la base de datos y cargar datos

Con un PostgreSQL ya disponible:

```bash
createdb educar_db
psql -d educar_db -f "Creacion_tablas.pgsql"
psql -d educar_db -f "Insercion_datosDB.pgsql"
```

Si no tenés PostgreSQL instalado a nivel sistema, el proyecto puede usar un
cluster local dentro de la carpeta `.pgdata/` (no requiere sudo):

```bash
pg_ctl -D .pgdata -l .pgdata/server.log start   # iniciar
createdb -h 127.0.0.1 -U postgres educar_db
psql -h 127.0.0.1 -U postgres -d educar_db -f "Creacion_tablas.pgsql"
psql -h 127.0.0.1 -U postgres -d educar_db -f "Insercion_datosDB.pgsql"
```

### 4. Ejecutar la aplicación

API + interfaz web en un único proceso:

```bash
uv run python frontend/run.py
```

- Web: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs

Solo interfaz Flet (requiere el backend corriendo aparte):

```bash
uv run flet run
```

## Usuarios de prueba

Contraseña para todos: `password123`

| Usuario      | Rol      |
| ------------ | -------- |
| `admin_gral` | ADMIN    |
| `admin2`     | ADMIN    |
| `lgomez`     | TEACHER  |
| `cruiz`      | TEACHER  |
| `rmartinez`  | PARENT   |
| `aperez`     | PARENT   |
| `tmartinez`  | STUDENT  |
| `mperez`     | STUDENT  |

Excepción: `admin2` usa la contraseña `admin1234`.

Si un usuario administrador no puede iniciar sesión, `fix_auth.py` regenera su
contraseña a `password123`:

```bash
uv run python fix_auth.py
```

## Tests

```bash
uv run pytest
```

Los tests de integración usan una base de datos aparte (`educar_test`, se crea
automáticamente si no existe) para no modificar `educar_db`. La URL se puede
personalizar con la variable de entorno `TEST_DATABASE_URL`.

## Build (empaquetado)

```bash
uv run flet build apk -v      # Android
uv run flet build ipa -v      # iOS
uv run flet build linux -v    # Linux (y macos / windows según SO)
uv run flet build web -v      # Web
```
