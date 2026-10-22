"""Tests de CRUD de catálogos (PUT/DELETE) y de los reportes Excel."""


def test_eliminar_nivel_con_cursos_asociados_devuelve_409(client, cabeceras_admin):
    nivel = client.post(
        "/api/v1/academico/niveles",
        json={"nombre": "Nivel Con Cursos"},
        headers=cabeceras_admin,
    )
    assert nivel.status_code == 201
    id_nivel = nivel.json()["id_nivel"]

    curso = client.post(
        "/api/v1/academico/cursos",
        json={"nombre": "Curso Dependiente", "id_nivel": id_nivel},
        headers=cabeceras_admin,
    )
    assert curso.status_code == 201
    id_curso = curso.json()["id_curso"]

    bloqueado = client.delete(
        f"/api/v1/academico/niveles/{id_nivel}", headers=cabeceras_admin
    )
    assert bloqueado.status_code == 409

    assert (
        client.delete(
            f"/api/v1/academico/cursos/{id_curso}", headers=cabeceras_admin
        ).status_code
        == 200
    )
    assert (
        client.delete(
            f"/api/v1/academico/niveles/{id_nivel}", headers=cabeceras_admin
        ).status_code
        == 200
    )


def test_crud_completo_de_curso(client, cabeceras_admin):
    nivel = client.post(
        "/api/v1/academico/niveles",
        json={"nombre": "Nivel Para Curso"},
        headers=cabeceras_admin,
    ).json()

    curso = client.post(
        "/api/v1/academico/cursos",
        json={"nombre": "7° Grado A", "id_nivel": nivel["id_nivel"]},
        headers=cabeceras_admin,
    )
    assert curso.status_code == 201
    id_curso = curso.json()["id_curso"]

    actualizado = client.put(
        f"/api/v1/academico/cursos/{id_curso}",
        json={"nombre": "7° Grado B"},
        headers=cabeceras_admin,
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["nombre"] == "7° Grado B"

    assert (
        client.delete(
            f"/api/v1/academico/cursos/{id_curso}", headers=cabeceras_admin
        ).status_code
        == 200
    )
    assert (
        client.delete(
            f"/api/v1/academico/niveles/{nivel['id_nivel']}", headers=cabeceras_admin
        ).status_code
        == 200
    )


def test_crud_completo_de_materia(client, cabeceras_admin):
    materia = client.post(
        "/api/v1/academico/materias",
        json={"nombre": "Música"},
        headers=cabeceras_admin,
    )
    assert materia.status_code == 201
    id_materia = materia.json()["id_materia"]

    actualizada = client.put(
        f"/api/v1/academico/materias/{id_materia}",
        json={"nombre": "Música y Expresión Artística"},
        headers=cabeceras_admin,
    )
    assert actualizada.status_code == 200

    assert (
        client.delete(
            f"/api/v1/academico/materias/{id_materia}", headers=cabeceras_admin
        ).status_code
        == 200
    )


def test_crud_completo_de_horario(client, cabeceras_admin):
    horario = client.post(
        "/api/v1/academico/horarios",
        json={"descripcion": "Turno Noche (19:30 - 22:00)"},
        headers=cabeceras_admin,
    )
    assert horario.status_code == 201
    id_horario = horario.json()["id_horario"]

    actualizado = client.put(
        f"/api/v1/academico/horarios/{id_horario}",
        json={"descripcion": "Turno Nocturno (20:00 - 22:30)"},
        headers=cabeceras_admin,
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["descripcion"] == "Turno Nocturno (20:00 - 22:30)"

    assert (
        client.delete(
            f"/api/v1/academico/horarios/{id_horario}", headers=cabeceras_admin
        ).status_code
        == 200
    )


def test_asignacion_de_materia_curso_profesor(client, cabeceras_admin):
    nivel = client.post(
        "/api/v1/academico/niveles",
        json={"nombre": "Nivel Asignación"},
        headers=cabeceras_admin,
    ).json()
    curso = client.post(
        "/api/v1/academico/cursos",
        json={"nombre": "Curso Asignación", "id_nivel": nivel["id_nivel"]},
        headers=cabeceras_admin,
    ).json()
    materia = client.post(
        "/api/v1/academico/materias",
        json={"nombre": "Materia Asignación"},
        headers=cabeceras_admin,
    ).json()

    asignacion = client.post(
        "/api/v1/academico/asignaciones",
        json={
            "id_materia": materia["id_materia"],
            "id_curso": curso["id_curso"],
            "legajo_profesor": 9001,
        },
        headers=cabeceras_admin,
    )
    assert asignacion.status_code == 201

    detalle = client.get("/api/v1/academico/asignaciones", headers=cabeceras_admin)
    assert detalle.status_code == 200

    eliminar = client.delete(
        f"/api/v1/academico/asignaciones/{materia['id_materia']}/{curso['id_curso']}",
        headers=cabeceras_admin,
    )
    assert eliminar.status_code == 200

    assert (
        client.delete(
            f"/api/v1/academico/materias/{materia['id_materia']}",
            headers=cabeceras_admin,
        ).status_code
        == 200
    )
    assert (
        client.delete(
            f"/api/v1/academico/cursos/{curso['id_curso']}", headers=cabeceras_admin
        ).status_code
        == 200
    )
    assert (
        client.delete(
            f"/api/v1/academico/niveles/{nivel['id_nivel']}", headers=cabeceras_admin
        ).status_code
        == 200
    )


REPORTES = [
    "alumnos",
    "cursos-materias",
    "deportes",
    "transporte",
    "solicitudes",
    "resumen",
]

CONTENT_TYPE_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_reportes_excel_se_descargan_como_admin(client, token_admin):
    for nombre in REPORTES:
        respuesta = client.get(f"/api/v1/reportes/{nombre}.xlsx?token={token_admin}")
        assert respuesta.status_code == 200, nombre
        assert respuesta.headers["content-type"].startswith(CONTENT_TYPE_XLSX), nombre
        assert respuesta.content[:2] == b"PK", nombre
        assert len(respuesta.content) > 1000, nombre


def test_reportes_exigen_token(client):
    respuesta = client.get("/api/v1/reportes/alumnos.xlsx")
    assert respuesta.status_code == 401


def test_reportes_solo_para_admin(client, token_profesor):
    respuesta = client.get(f"/api/v1/reportes/resumen.xlsx?token={token_profesor}")
    assert respuesta.status_code == 403
