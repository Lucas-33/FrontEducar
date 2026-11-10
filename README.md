# Educar para Transformar

Sistema de gestión escolar: **API REST (FastAPI) + interfaz web (Flet) sobre PostgreSQL**.

- `backend/` → API REST (FastAPI + SQLAlchemy): autenticación JWT, personas, académico, servicios escolares.
- `frontend/` → Interfaz (Flet) montada sobre el mismo proceso FastAPI y cliente HTTP (`api_client.py`).
- `Creacion_tablas.pgsql` / `Insercion_datosDB.pgsql` → scripts de esquema y datos de prueba.

## Funcionalidades

- **Seguridad**: login JWT, control de acceso por rol (ADMIN, TEACHER, PARENT, STUDENT), cambio de contraseña y usuarios vinculados a alumnos, docentes o tutores.
- **Gestión académica**: ABM de niveles, cursos, materias, horarios y asignaciones docente-materia-curso. La matriculación de alumnos y la aprobación de admisiones validan que la edad coincida con el grado/nivel solicitado.
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

## Deploy en Render + Neon

La aplicación se ejecuta en **un único servicio web de Render** (FastAPI + Flet)
y usa **PostgreSQL alojado en Neon**. La configuración declarativa del servicio
está en `render.yaml`.

### 1. Crear la base de datos en Neon

1. Entrá a [neon.tech](https://neon.tech), creá un proyecto y elegí una región
   cercana a Render (por ejemplo, `US West (Oregon)`).
2. En **Connect** copiá la **Pooled connection string**. Tiene un formato similar a:

   ```text
   postgresql://usuario:clave@ep-xxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

3. Guardala: se usa como `DATABASE_URL` en Render.

### 2. Crear el esquema y los datos iniciales en Neon

Opción recomendada (no requiere `psql`):

```bash
DATABASE_URL='postgresql://usuario:clave@ep-xxx-pooler...neon.tech/neondb?sslmode=require' \
  uv run python scripts/init_db.py --reset
```

Opción con `psql`:

```bash
psql "$DATABASE_URL" -f Creacion_tablas.pgsql
psql "$DATABASE_URL" -f Insercion_datosDB.pgsql
```

> `--reset` elimina las tablas existentes antes de recrearlas. Usalo solo la
> primera vez o cuando quieras reiniciar los datos. Si la base ya tiene datos,
> ejecutá el script sin `--reset` (se niega a pisar una base existente).
>
> Los scripts crean los usuarios demo (`admin_gral` / `password123`, etc.).

### 3. Subir los cambios a GitHub

```bash
git add .
git commit -m "Configura deploy en Render + Neon"
git push origin deploy
```

### 4. Crear el servicio en Render

1. En el panel de Render: **New +** → **Blueprint**.
2. Conectá el repositorio `Lucas-33/FrontEducar`.
3. Seleccioná la rama `deploy`.
4. Render detecta `render.yaml` y pide `DATABASE_URL`: pegá la pooled connection
   string de Neon.
5. Aplicá los cambios. `SECRET_KEY` se genera automáticamente.

Si preferís crear el servicio manualmente (**New +** → **Web Service**):

- **Runtime**: Python 3 (toma la versión de `.python-version`, 3.12).
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**:

  ```bash
  uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips "*"
  ```

- **Environment**:
  - `DATABASE_URL` → connection string de Neon.
  - `SECRET_KEY` → una clave segura (o usá “Generate”).
  - `ACCESS_TOKEN_EXPIRE_MINUTES=1440` (opcional).
  - `API_BASE_URL` → opcional; normalmente no hace falta.
- **Health Check Path**: `/api/v1/health`

### 5. Verificar el deploy

- App: `https://<tu-servicio>.onrender.com/`
- Salud: `https://<tu-servicio>.onrender.com/api/v1/health`
- Swagger: `https://<tu-servicio>.onrender.com/docs`
- Login demo: `admin_gral` / `password123`

### Notas

- **No subas `.env`**: en Render la configuración va en *Environment*.
- La app crea las tablas faltantes al iniciar, pero **no carga los datos demo**;
  eso se hace una vez con `scripts/init_db.py`.
- Neon suspende la base por inactividad y Render duerme el servicio en el plan
  free. La primera petición puede tardar unos segundos.
- `DATABASE_URL` puede venir como `postgresql://` o `postgres://`; la app la
  normaliza automáticamente al driver `psycopg2`.
- `RENDER_EXTERNAL_URL` se agrega solo a CORS. Si usás un dominio propio,
  agregalo en `CORS_ORIGINS` separado por comas.
- `render.yaml` asume la rama `deploy` y la región `oregon`. Ajustá `branch` y
  `region` si tu repositorio o ubicación son distintos.

## Tests

```bash
uv run pytest
```

Los tests de integración usan una base de datos aparte (`educar_test`, se crea
automáticamente si no existe) para no modificar `educar_db`. La URL se puede
personalizar con la variable de entorno `TEST_DATABASE_URL`.

## Build (empaquetado)

La app Flet está en `frontend/` (entry point `frontend/main.py`). Para
empaquetar se pasa ese directorio para que solo se incluyan las dependencias
de la interfaz (`flet` + `httpx`); las dependencias del backend
(`psycopg2`, `bcrypt`, etc.) no tienen wheels de Android y no van en el APK:

```bash
uv run flet build apk frontend --python-version 3.12   # Android (.apk)
uv run flet build aab frontend --python-version 3.12   # Android (.aab, Play Store)
uv run flet build web frontend -v                      # Web
```

> iOS (`ipa`) requiere compilar en macOS con Xcode.

El resultado queda en `frontend/build/apk/`. Con `--split-per-abi` se genera
un APK por arquitectura (menor tamaño). La primera compilación tarda varios
minutos (Gradle descarga artefactos de Android).

### Requisitos del toolchain (Android)

`flet build apk` necesita **JDK 17**, el **Android SDK** y el **Flutter SDK
3.44.8** (la versión exacta que exige Flet 0.86.5). Si falta algo, el CLI lo
descarga e instala automáticamente en:

| Componente     | Ruta                                  |
| -------------- | ------------------------------------- |
| JDK 17.0.13+11 | `~/java/17.0.13+11`                   |
| Android SDK    | `~/Android/sdk`                       |
| Flutter 3.44.8 | `~/flutter/3.44.8`                    |

También se puede instalar a mano (mismas rutas para que flet los detecte):

```bash
# JDK 17 (Temurin)
curl -LO https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.13%2B11/OpenJDK17U-jdk_x64_linux_hotspot_17.0.13_11.tar.gz
mkdir -p ~/java/17.0.13+11 && tar -xzf OpenJDK17U-jdk_x64_linux_hotspot_17.0.13_11.tar.gz -C ~/java/17.0.13+11 --strip-components=1

# Android cmdline-tools
curl -LO https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
mkdir -p ~/Android/sdk/cmdline-tools && unzip commandlinetools-linux-11076708_latest.zip -d ~/Android/sdk/cmdline-tools
mv ~/Android/sdk/cmdline-tools/cmdline-tools ~/Android/sdk/cmdline-tools/latest

# Paquetes mínimos + extras requeridos por Flutter 3.44 + licencias
export JAVA_HOME=~/java/17.0.13+11
yes | ~/Android/sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=$HOME/Android/sdk "platform-tools" "platforms;android-35" "build-tools;34.0.0"
yes | ~/Android/sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=$HOME/Android/sdk "platforms;android-36" "build-tools;36.0.0" "ndk;28.2.13676358"
yes | ~/Android/sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=$HOME/Android/sdk --licenses

# Flutter 3.44.8
curl -LO https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.44.8-stable.tar.xz
mkdir -p ~/flutter/3.44.8 && tar -xf flutter_linux_3.44.8-stable.tar.xz -C ~/flutter/3.44.8 --strip-components=1
```

### Backend en el móvil

La app móvil consume la API con `API_BASE_URL` (ver
`frontend/app/api_client.py`). El APK usa por defecto el backend de
producción (`https://educar-para-transformar-zcuo.onrender.com/api/v1`);
en desarrollo local sigue usando `127.0.0.1` automáticamente.

### Ajuste de memoria de Gradle

Flet configura Gradle por defecto con `-Xmx8G`, pensado para máquinas con
mucha RAM; en equipos con ~8 GB el OOM killer puede matar el daemon de
Gradle a mitad de compilación ("Gradle build daemon disappeared
unexpectedly"). El override en `frontend/pyproject.toml`
(`[tool.flet.android.gradle_properties]`) lo limita a valores seguros para
esta máquina. Si el build falla por memoria, ajustar `org.gradle.jvmargs`
ahí.

El template de build de Flet 0.86.5 fija `jni: 1.0.0`, incompatible con
los bindings de `shared_preferences_android` actuales (necesitan `jni
^1.1.0`). El script `scripts/patch_flet_template.py` corrige el template
cacheado en `~/.flet/cache/` (idempotente):

```bash
uv run python scripts/patch_flet_template.py
```

Solo hace falta correrlo una vez por máquina (o después de borrar el
cache de Flet) y requiere haber corrido `flet build` al menos una vez
para que el template esté cacheado.

