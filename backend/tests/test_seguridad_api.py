"""Tests de autenticación, autorización por rol y cambio de contraseña."""
from backend.tests.conftest import PASSWORD_PRUEBA


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
