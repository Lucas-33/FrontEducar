"""Tests de calificaciones y asistencia (módulo de evaluación)."""

from backend.tests.conftest import LEGAJO_ALUMNO_1, LEGAJO_ALUMNO_2, LEGAJO_PROFESOR


def _crear_calificacion(client, cabeceras, **overrides):
    payload = {
        "legajo_alumno": LEGAJO_ALUMNO_1,
        "id_materia": 1,
        "id_curso": 1,
        "periodo": "1° Trimestre",
        "tipo": "Parcial",
        "nota": 8.5,
        "fecha": "2026-10-01",
        "observacion": "Creada por test automatizado",
    }
    payload.update(overrides)
    return client.post(
        "/api/v1/academico/calificaciones", json=payload, headers=cabeceras
    )


def test_docente_crea_calificacion_y_se_autoasigna(client, cabeceras_profesor):
    respuesta = _crear_calificacion(client, cabeceras_profesor, fecha="2026-10-02")
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nota"] == 8.5
    assert cuerpo["legajo_profesor"] == LEGAJO_PROFESOR


def test_alumno_solo_ve_sus_propias_calificaciones(
    client, cabeceras_profesor, cabeceras_alumno
):
    propia = _crear_calificacion(client, cabeceras_profesor, fecha="2026-10-03")
    ajena = _crear_calificacion(
        client,
        cabeceras_profesor,
        legajo_alumno=LEGAJO_ALUMNO_2,
        fecha="2026-10-04",
        observacion=None,
    )
    assert propia.status_code == 201 and ajena.status_code == 201

    listado = client.get("/api/v1/academico/calificaciones", headers=cabeceras_alumno)
    assert listado.status_code == 200
    ids = [c["id_calificacion"] for c in listado.json()]
    assert propia.json()["id_calificacion"] in ids
    assert ajena.json()["id_calificacion"] not in ids
    assert all(c["legajo_alumno"] == LEGAJO_ALUMNO_1 for c in listado.json())


def test_padre_accede_solo_a_las_calificaciones_de_sus_hijos(
    client, cabeceras_profesor, cabeceras_padre
):
    _crear_calificacion(client, cabeceras_profesor, fecha="2026-10-05")

    propias = client.get(
        f"/api/v1/academico/calificaciones?legajo_alumno={LEGAJO_ALUMNO_1}",
        headers=cabeceras_padre,
    )
    assert propias.status_code == 200
    assert all(c["legajo_alumno"] == LEGAJO_ALUMNO_1 for c in propias.json())

    ajenas = client.get(
        f"/api/v1/academico/calificaciones?legajo_alumno={LEGAJO_ALUMNO_2}",
        headers=cabeceras_padre,
    )
    assert ajenas.status_code == 403


def test_actualizar_y_eliminar_calificacion(
    client, cabeceras_profesor, cabeceras_alumno, cabeceras_admin
):
    creada = _crear_calificacion(
        client, cabeceras_profesor, fecha="2026-10-06", nota=6.0
    )
    assert creada.status_code == 201
    id_calificacion = creada.json()["id_calificacion"]

    actualizada = client.put(
        f"/api/v1/academico/calificaciones/{id_calificacion}",
        json={"nota": 9.25, "observacion": "Nota rectificada"},
        headers=cabeceras_profesor,
    )
    assert actualizada.status_code == 200
    assert actualizada.json()["nota"] == 9.25

    visibles = client.get(
        "/api/v1/academico/calificaciones", headers=cabeceras_alumno
    ).json()
    coincidencia = [c for c in visibles if c["id_calificacion"] == id_calificacion]
    assert coincidencia and coincidencia[0]["nota"] == 9.25

    eliminada = client.delete(
        f"/api/v1/academico/calificaciones/{id_calificacion}",
        headers=cabeceras_admin,
    )
    assert eliminada.status_code == 200

    visibles = client.get(
        "/api/v1/academico/calificaciones", headers=cabeceras_alumno
    ).json()
    assert all(c["id_calificacion"] != id_calificacion for c in visibles)


def test_alumno_no_puede_registrar_calificaciones(client, cabeceras_alumno):
    respuesta = _crear_calificacion(client, cabeceras_alumno, fecha="2026-10-07")
    assert respuesta.status_code == 403


def test_nota_fuera_de_rango_devuelve_422(client, cabeceras_profesor):
    respuesta = _crear_calificacion(
        client, cabeceras_profesor, fecha="2026-10-08", nota=12
    )
    assert respuesta.status_code == 422


def test_asistencia_lote_es_upsert_y_aislamiento_por_rol(
    client,
    cabeceras_profesor,
    cabeceras_alumno,
    cabeceras_padre,
    cabeceras_admin,
):
    fecha = "2026-10-09"
    lote = client.post(
        "/api/v1/academico/asistencia/lote",
        json={
            "id_curso": 1,
            "fecha": fecha,
            "registros": [
                {"legajo_alumno": LEGAJO_ALUMNO_1, "estado": "PRESENTE"},
                {"legajo_alumno": LEGAJO_ALUMNO_2, "estado": "AUSENTE"},
            ],
        },
        headers=cabeceras_profesor,
    )
    assert lote.status_code == 200
    assert len(lote.json()) == 2

    # Reenviar el lote del mismo día actualiza el estado (no duplica)
    relote = client.post(
        "/api/v1/academico/asistencia/lote",
        json={
            "id_curso": 1,
            "fecha": fecha,
            "registros": [
                {
                    "legajo_alumno": LEGAJO_ALUMNO_1,
                    "estado": "TARDE",
                    "observacion": "Llegó tarde",
                },
            ],
        },
        headers=cabeceras_profesor,
    )
    assert relote.status_code == 200
    assert len(relote.json()) == 2
    registro_1 = next(r for r in relote.json() if r["legajo_alumno"] == LEGAJO_ALUMNO_1)
    assert registro_1["estado"] == "TARDE"
    id_registro_1 = registro_1["id_asistencia"]

    # El alumno solo ve su propia asistencia
    propias = client.get("/api/v1/academico/asistencia", headers=cabeceras_alumno)
    assert propias.status_code == 200
    assert all(r["legajo_alumno"] == LEGAJO_ALUMNO_1 for r in propias.json())

    # El tutor ve la de su hijo, pero no la de otro alumno
    assert (
        client.get(
            f"/api/v1/academico/asistencia?legajo_alumno={LEGAJO_ALUMNO_1}",
            headers=cabeceras_padre,
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/api/v1/academico/asistencia?legajo_alumno={LEGAJO_ALUMNO_2}",
            headers=cabeceras_padre,
        ).status_code
        == 403
    )

    # Resumen de presentismo
    resumen = client.get(
        f"/api/v1/academico/asistencia/resumen/{LEGAJO_ALUMNO_1}",
        headers=cabeceras_alumno,
    )
    assert resumen.status_code == 200
    cuerpo = resumen.json()
    assert cuerpo["total"] >= 1
    assert cuerpo["tardes"] >= 1
    assert 0 <= cuerpo["porcentaje_presentismo"] <= 100
    assert (
        client.get(
            f"/api/v1/academico/asistencia/resumen/{LEGAJO_ALUMNO_2}",
            headers=cabeceras_padre,
        ).status_code
        == 403
    )

    # Eliminar el registro como ADMIN lo quita del listado
    eliminar = client.delete(
        f"/api/v1/academico/asistencia/{id_registro_1}",
        headers=cabeceras_admin,
    )
    assert eliminar.status_code == 200
    restantes = client.get(
        f"/api/v1/academico/asistencia?id_curso=1&fecha={fecha}",
        headers=cabeceras_admin,
    ).json()
    assert all(r["id_asistencia"] != id_registro_1 for r in restantes)
