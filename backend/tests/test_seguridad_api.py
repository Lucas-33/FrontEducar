"""Tests de autenticación, autorización por rol y cambio de contraseña."""

from backend.tests.conftest import (
    LEGAJO_ALUMNO_1,
    LEGAJO_ALUMNO_2,
    PASSWORD_PRUEBA,
)


def test_login_correcto_y_perfil(client):
    respuesta = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_test", "password": PASSWORD_PRUEBA},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["access_token"]
    assert cuerpo["rol"] == "ADMIN"
    assert cuerpo["username"] == "admin_test"

    perfil = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {cuerpo['access_token']}"},
    )
    assert perfil.status_code == 200
    assert perfil.json()["username"] == "admin_test"
    assert perfil.json()["rol"] == "ADMIN"


def test_login_con_password_incorrecta(client):
    respuesta = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_test", "password": "incorrecta"},
    )
    assert respuesta.status_code == 401


def test_acceso_sin_token_devuelve_401(client):
    assert client.get("/api/v1/academico/cursos").status_code == 401
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/personas/alumnos").status_code == 401


def test_token_invalido_devuelve_401(client):
    respuesta = client.get(
        "/api/v1/academico/cursos",
        headers={"Authorization": "Bearer token-falso.invalido.xyz"},
    )
    assert respuesta.status_code == 401


def test_escritura_de_catalogos_restringida_a_admin(client, cabeceras_profesor):
    respuesta = client.post(
        "/api/v1/academico/niveles",
        json={"nombre": "Nivel Prohibido"},
        headers=cabeceras_profesor,
    )
    assert respuesta.status_code == 403


def test_crud_de_nivel_como_admin(client, cabeceras_admin):
    crear = client.post(
        "/api/v1/academico/niveles",
        json={"nombre": "Nivel Temporal"},
        headers=cabeceras_admin,
    )
    assert crear.status_code == 201
    id_nivel = crear.json()["id_nivel"]

    actualizar = client.put(
        f"/api/v1/academico/niveles/{id_nivel}",
        json={"nombre": "Nivel Temporal Editado"},
        headers=cabeceras_admin,
    )
    assert actualizar.status_code == 200
    assert actualizar.json()["nombre"] == "Nivel Temporal Editado"

    eliminar = client.delete(
        f"/api/v1/academico/niveles/{id_nivel}",
        headers=cabeceras_admin,
    )
    assert eliminar.status_code == 200


def test_cambio_de_password(client, cabeceras_admin):
    crear_usuario = client.post(
        "/api/v1/auth/usuarios",
        json={
            "username": "pw_test",
            "password": "inicial123",
            "id_rol": 4,
            "activo": True,
        },
        headers=cabeceras_admin,
    )
    assert crear_usuario.status_code == 201

    login_inicial = client.post(
        "/api/v1/auth/login",
        json={"username": "pw_test", "password": "inicial123"},
    )
    assert login_inicial.status_code == 200
    token = login_inicial.json()["access_token"]

    cambiar = client.put(
        "/api/v1/auth/me/password",
        json={"password_actual": "inicial123", "password_nueva": "nueva456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cambiar.status_code == 200

    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": "pw_test", "password": "inicial123"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": "pw_test", "password": "nueva456"},
        ).status_code
        == 200
    )

    # Con la contraseña vieja ya no puede autenticarse para cambiarla de nuevo
    rechazo = client.put(
        "/api/v1/auth/me/password",
        json={"password_actual": "inicial123", "password_nueva": "otra789"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rechazo.status_code in (400, 401)


def test_alumno_y_tutor_solo_ven_sus_propias_fichas(
    client, cabeceras_alumno, cabeceras_padre
):
    propia = client.get(
        f"/api/v1/personas/alumnos/{LEGAJO_ALUMNO_1}",
        headers=cabeceras_alumno,
    )
    assert propia.status_code == 200
    assert propia.json()["legajo"] == LEGAJO_ALUMNO_1

    ajena = client.get(
        f"/api/v1/personas/alumnos/{LEGAJO_ALUMNO_2}",
        headers=cabeceras_alumno,
    )
    assert ajena.status_code == 403

    hijo = client.get(
        f"/api/v1/personas/alumnos/{LEGAJO_ALUMNO_1}",
        headers=cabeceras_padre,
    )
    assert hijo.status_code == 200

    ajeno = client.get(
        f"/api/v1/personas/alumnos/{LEGAJO_ALUMNO_2}",
        headers=cabeceras_padre,
    )
    assert ajeno.status_code == 403


def test_admin_edita_usuario_correo_y_vinculo(client, cabeceras_admin):
    crear = client.post(
        "/api/v1/auth/usuarios",
        json={
            "username": "edit_test",
            "password": PASSWORD_PRUEBA,
            "id_rol": 4,
            "activo": True,
        },
        headers=cabeceras_admin,
    )
    assert crear.status_code == 201
    id_usuario = crear.json()["id_usuario"]

    actualizar = client.put(
        f"/api/v1/auth/usuarios/{id_usuario}",
        json={
            "username": "edit_test_nuevo",
            "id_rol": 4,
            "legajo_alumno": LEGAJO_ALUMNO_2,
            "legajo_profesor": None,
            "id_padre": None,
        },
        headers=cabeceras_admin,
    )
    assert actualizar.status_code == 200
    cuerpo = actualizar.json()
    assert cuerpo["username"] == "edit_test_nuevo"
    assert cuerpo["legajo_alumno"] == LEGAJO_ALUMNO_2
    assert cuerpo["legajo_profesor"] is None
    assert cuerpo["id_padre"] is None

    # El nuevo usuario de acceso ya es el que autentica.
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": "edit_test", "password": PASSWORD_PRUEBA},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/api/v1/auth/login",
            json={"username": "edit_test_nuevo", "password": PASSWORD_PRUEBA},
        ).status_code
        == 200
    )

    desvincular = client.put(
        f"/api/v1/auth/usuarios/{id_usuario}",
        json={"legajo_alumno": None},
        headers=cabeceras_admin,
    )
    assert desvincular.status_code == 200
    assert desvincular.json()["legajo_alumno"] is None

    inexistente = client.put(
        f"/api/v1/auth/usuarios/{id_usuario}",
        json={"legajo_alumno": 999999},
        headers=cabeceras_admin,
    )
    assert inexistente.status_code == 404
