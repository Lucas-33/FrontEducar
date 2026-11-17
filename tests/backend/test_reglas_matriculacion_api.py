"""Tests de integración de las reglas de edad en altas y admisiones."""

from datetime import date

from sqlalchemy.orm import sessionmaker

from backend.app.models.comunidad import SolicitudInscripcion


def _crear_curso(client, cabeceras_admin, nombre: str, id_nivel: int | None = None):
    if id_nivel is None:
        nivel = client.post(
            "/api/v1/academico/niveles",
            json={"nombre": f"Primario Test {nombre}"},
            headers=cabeceras_admin,
        )
        assert nivel.status_code == 201, nivel.text
        id_nivel = nivel.json()["id_nivel"]

    curso = client.post(
        "/api/v1/academico/cursos",
        json={"nombre": nombre, "id_nivel": id_nivel},
        headers=cabeceras_admin,
    )
    assert curso.status_code == 201, curso.text
    return curso.json()


def _payload_alumno(dni: str, id_curso: int, edad: int) -> dict:
    return {
        "dni": dni,
        "nombre": "Alumno",
        "apellido": "De Prueba",
        "fecha_nacimiento": f"{date.today().year - edad}-01-01",
        "domicilio": "Calle de Prueba 123",
        "id_curso": id_curso,
    }


def test_alta_de_alumno_rechaza_edad_incompatible_con_el_grado(
    client, cabeceras_admin
):
    curso = _crear_curso(client, cabeceras_admin, "1° Grado A")

    respuesta = client.post(
        "/api/v1/personas/alumnos",
        json=_payload_alumno("59000001", curso["id_curso"], edad=20),
        headers=cabeceras_admin,
    )

    assert respuesta.status_code == 400
    assert "no corresponde a su edad" in respuesta.json()["detail"]


def test_alta_de_alumno_permite_edad_correspondiente(client, cabeceras_admin):
    curso = _crear_curso(client, cabeceras_admin, "2° Grado A")

    respuesta = client.post(
        "/api/v1/personas/alumnos",
        json=_payload_alumno("59000002", curso["id_curso"], edad=7),
        headers=cabeceras_admin,
    )

    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["id_curso"] == curso["id_curso"]


def test_actualizacion_rechaza_curso_incompatible_con_la_edad(
    client, cabeceras_admin
):
    curso_primario = _crear_curso(client, cabeceras_admin, "3° Grado A")
    curso_secundario = _crear_curso(
        client, cabeceras_admin, "5° Año A", id_nivel=1
    )

    alta = client.post(
        "/api/v1/personas/alumnos",
        json=_payload_alumno("59000003", curso_primario["id_curso"], edad=8),
        headers=cabeceras_admin,
    )
    assert alta.status_code == 201, alta.text
    legajo = alta.json()["legajo"]

    cambio_curso = client.put(
        f"/api/v1/personas/alumnos/{legajo}",
        json={"id_curso": curso_secundario["id_curso"]},
        headers=cabeceras_admin,
    )
    assert cambio_curso.status_code == 400
    assert "no corresponde a su edad" in cambio_curso.json()["detail"]

    cambio_fecha = client.put(
        f"/api/v1/personas/alumnos/{legajo}",
        json={"fecha_nacimiento": f"{date.today().year - 20}-01-01"},
        headers=cabeceras_admin,
    )
    assert cambio_fecha.status_code == 400
    assert "no corresponde a su edad" in cambio_fecha.json()["detail"]


def test_solicitud_publica_rechaza_postulante_mayor_para_el_nivel(client):
    respuesta = client.post(
        "/api/v1/comunidad/solicitudes",
        json={
            "postulante": "Postulante Mayor",
            "dni": "59000004",
            "fecha_nacimiento": f"{date.today().year - 25}-01-01",
            "nivel": "Inicial - Sala de 4",
            "tutor": "Tutor de Prueba",
        },
    )

    assert respuesta.status_code == 400
    assert "no corresponde a su edad" in respuesta.json()["detail"]


def test_solicitud_publica_exige_fecha_de_nacimiento(client):
    respuesta = client.post(
        "/api/v1/comunidad/solicitudes",
        json={
            "postulante": "Postulante Sin Fecha",
            "dni": "59000005",
            "nivel": "Primario - 1° Grado",
            "tutor": "Tutor de Prueba",
        },
    )

    assert respuesta.status_code == 422


def test_aprobacion_revalida_edad_de_solicitudes_antiguas(
    client, cabeceras_admin, engine_prueba
):
    session = sessionmaker(bind=engine_prueba)()
    try:
        solicitud = SolicitudInscripcion(
            postulante="Solicitud Antigua",
            dni="59000006",
            fecha_nacimiento=f"{date.today().year - 40}-01-01",
            nivel="Primario - 1° Grado",
            tutor="Tutor Antiguo",
            estado="Pendiente",
        )
        session.add(solicitud)
        session.commit()
        session.refresh(solicitud)
        id_solicitud = solicitud.id_solicitud
    finally:
        session.close()

    respuesta = client.put(
        f"/api/v1/comunidad/solicitudes/{id_solicitud}/estado",
        json={"estado": "Aprobado"},
        headers=cabeceras_admin,
    )

    assert respuesta.status_code == 400
    assert "no corresponde a su edad" in respuesta.json()["detail"]


def test_inscripcion_deportiva_rechaza_grupo_de_otro_nivel(
    client, cabeceras_admin
):
    curso = _crear_curso(client, cabeceras_admin, "Sala de 4 A")

    alta = client.post(
        "/api/v1/personas/alumnos",
        json=_payload_alumno("59000007", curso["id_curso"], edad=4),
        headers=cabeceras_admin,
    )
    assert alta.status_code == 201, alta.text
    legajo = alta.json()["legajo"]

    deporte = client.post(
        "/api/v1/servicios/deportes",
        json={"nombre": "Deporte Nivel Test"},
        headers=cabeceras_admin,
    )
    assert deporte.status_code == 201, deporte.text
    horario = client.post(
        "/api/v1/academico/horarios",
        json={"descripcion": "Turno Nivel Test"},
        headers=cabeceras_admin,
    )
    assert horario.status_code == 201, horario.text
    grupo = client.post(
        "/api/v1/servicios/deportes/grupos",
        json={
            "id_deporte": deporte.json()["id_deporte"],
            "id_nivel": 1,  # Secundario, distinto del curso Inicial del alumno
            "id_horario": horario.json()["id_horario"],
        },
        headers=cabeceras_admin,
    )
    assert grupo.status_code == 201, grupo.text

    respuesta = client.post(
        "/api/v1/servicios/deportes/inscripciones",
        json={"legajo_alumno": legajo, "id_grupo": grupo.json()["id_grupo"]},
        headers=cabeceras_admin,
    )

    assert respuesta.status_code == 400
    assert "nivel educativo" in respuesta.json()["detail"]
