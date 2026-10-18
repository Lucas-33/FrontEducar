"""Configuración de pytest para el backend.

Crea una base de datos PostgreSQL de prueba (por defecto `educar_test`),
genera el esquema desde los modelos SQLAlchemy, siembra datos mínimos y
reemplaza la dependencia `get_db` para que ningún test toque la base de
desarrollo (`educar_db`).

La URL se puede personalizar con la variable de entorno `TEST_DATABASE_URL`.
"""
import os
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from backend.app import models  # noqa: F401  (registra todas las tablas en Base.metadata)
from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app.models.academico import Curso, Materia, MateriaCursoProfesor, NivelEducativo
from backend.app.models.personas import Alumno, Padre, PadreAlumno, Profesor
from backend.app.models.seguridad import Rol, Usuario
from backend.app.services.seguridad import seguridad_service

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres@127.0.0.1:5432/educar_test",
)

PASSWORD_PRUEBA = "password123"

LEGAJO_ALUMNO_1 = 9001
LEGAJO_ALUMNO_2 = 9002
LEGAJO_PROFESOR = 9001
ID_PADRE = 9001


def _crear_base_si_falta():
    """Crea la base de datos de prueba conectándose a la base de mantenimiento."""
    url = make_url(TEST_DATABASE_URL)
    engine_admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with engine_admin.connect() as conexion:
            existe = conexion.exec_driver_sql(
                "SELECT 1 FROM pg_database WHERE datname = %s", (url.database,)
            ).scalar()
            if not existe:
                conexion.exec_driver_sql(f'CREATE DATABASE "{url.database}"')
    finally:
        engine_admin.dispose()


def _sembrar_datos(engine):
    """Datos mínimos y deterministas para los tests de integración."""
    session = sessionmaker(bind=engine)()
    try:
        hash_password = seguridad_service.get_password_hash(PASSWORD_PRUEBA)

        session.add_all(
            [
                Rol(id_rol=1, nombre="ADMIN"),
                Rol(id_rol=2, nombre="TEACHER"),
                Rol(id_rol=3, nombre="PARENT"),
                Rol(id_rol=4, nombre="STUDENT"),
            ]
        )
        session.flush()

        session.add(NivelEducativo(id_nivel=1, nombre="Secundario"))
        session.flush()

        session.add_all(
            [
                Curso(id_curso=1, nombre="1° Año A", id_nivel=1),
                Materia(id_materia=1, nombre="Matemática"),
            ]
        )
        session.flush()

        session.add(
            Profesor(
                legajo=LEGAJO_PROFESOR,
                dni="30000001",
                nombre="Ana",
                apellido="Prueba",
                especialidad="Matemática",
                correo_electronico="ana.prueba@educar.edu.ar",
                telefono="3624000001",
                estado="ACTIVO",
            )
        )
        session.add(
            Padre(
                id_padre=ID_PADRE,
                dni="20000001",
                nombre="Pedro",
                apellido="Prueba",
                telefono="3624000002",
                correo_electronico="pedro.prueba@gmail.com",
            )
        )
        session.flush()

        session.add_all(
            [
                Alumno(
                    legajo=LEGAJO_ALUMNO_1,
                    dni="50000001",
                    nombre="Lucía",
                    apellido="Prueba",
                    fecha_nacimiento=date(2013, 4, 10),
                    domicilio="Calle Prueba 123, Resistencia",
                    telefono="3624000002",
                    correo_electronico="lucia.prueba@alumno.educar.ar",
                    id_curso=1,
                    estado_alumno="ACTIVO",
                ),
                Alumno(
                    legajo=LEGAJO_ALUMNO_2,
                    dni="50000002",
                    nombre="Julián",
                    apellido="Prueba",
                    fecha_nacimiento=date(2013, 8, 22),
                    domicilio="Calle Prueba 456, Resistencia",
                    telefono="3624000003",
                    correo_electronico="julian.prueba@alumno.educar.ar",
                    id_curso=1,
                    estado_alumno="ACTIVO",
                ),
            ]
        )
        session.flush()

        session.add(PadreAlumno(id_padre=ID_PADRE, legajo_alumno=LEGAJO_ALUMNO_1))
        session.add(
            MateriaCursoProfesor(
                id_materia=1,
                id_curso=1,
                legajo_profesor=LEGAJO_PROFESOR,
            )
        )
        session.flush()

        session.add_all(
            [
                Usuario(
                    username="admin_test",
                    password_hash=hash_password,
                    id_rol=1,
                    activo=True,
                ),
                Usuario(
                    username="prof_test",
                    password_hash=hash_password,
                    id_rol=2,
                    legajo_profesor=LEGAJO_PROFESOR,
                    activo=True,
                ),
                Usuario(
                    username="papa_test",
                    password_hash=hash_password,
                    id_rol=3,
                    id_padre=ID_PADRE,
                    activo=True,
                ),
                Usuario(
                    username="alum_test",
                    password_hash=hash_password,
                    id_rol=4,
                    legajo_alumno=LEGAJO_ALUMNO_1,
                    activo=True,
                ),
            ]
        )
        session.commit()

        # Al insertar IDs explícitos, las secuencias de PostgreSQL quedan desfasadas.
        # Se ajustan para que los endpoints que crean registros nuevos no colisionen.
        tablas = [
            ("alumno", "legajo"),
            ("profesor", "legajo"),
            ("padre", "id_padre"),
            ("nivel_educativo", "id_nivel"),
            ("curso", "id_curso"),
            ("materia", "id_materia"),
        ]
        with engine.connect() as conexion:
            for tabla, pk in tablas:
                conexion.exec_driver_sql(
                    f"SELECT setval(pg_get_serial_sequence('{tabla}', '{pk}'), "
                    f"COALESCE(MAX({pk}), 1)) FROM {tabla}"
                )
            conexion.commit()
    finally:
        session.close()


@pytest.fixture(scope="session")
def engine_prueba():
    """Motor de la base de datos de prueba con esquema limpio y datos sembrados."""
    try:
        _crear_base_si_falta()
    except Exception as error:  # pragma: no cover - depende del entorno
        pytest.skip(f"PostgreSQL no disponible para los tests de integración: {error}")

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    _sembrar_datos(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def _override_get_db(engine_prueba):
    """Redirige la dependencia get_db de FastAPI a la base de prueba."""
    session_prueba = sessionmaker(autocommit=False, autoflush=False, bind=engine_prueba)

    def get_db_prueba():
        db = session_prueba()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_prueba
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client(engine_prueba):
    """Cliente HTTP de pruebas con la dependencia de base de datos reemplazada."""
    with TestClient(app) as test_client:
        yield test_client


def _login(client: TestClient, username: str) -> str:
    respuesta = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD_PRUEBA},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


@pytest.fixture(scope="session")
def token_admin(client) -> str:
    return _login(client, "admin_test")


@pytest.fixture(scope="session")
def token_profesor(client) -> str:
    return _login(client, "prof_test")


@pytest.fixture(scope="session")
def token_alumno(client) -> str:
    return _login(client, "alum_test")


@pytest.fixture(scope="session")
def token_padre(client) -> str:
    return _login(client, "papa_test")


@pytest.fixture()
def cabeceras_admin(token_admin) -> dict:
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture()
def cabeceras_profesor(token_profesor) -> dict:
    return {"Authorization": f"Bearer {token_profesor}"}


@pytest.fixture()
def cabeceras_alumno(token_alumno) -> dict:
    return {"Authorization": f"Bearer {token_alumno}"}


@pytest.fixture()
def cabeceras_padre(token_padre) -> dict:
    return {"Authorization": f"Bearer {token_padre}"}
