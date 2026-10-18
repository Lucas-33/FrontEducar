"""Tests de los formularios públicos y la moderación de la comunidad."""


def _crear_solicitud(client, postulante="Test Alumno Solicitud"):
    return client.post(
        "/api/v1/comunidad/solicitudes",
        json={
            "postulante": postulante,
            "dni": "55123456",
            "fecha_nacimiento": "2021-03-10",
            "nivel": "Inicial (Sala de 5)",
            "tutor": "Tutor de Prueba",
            "telefono": "3624000099",
            "correo": "tutor.prueba@gmail.com",
        },
    )


def test_solicitud_de_inscripcion_flujo_completo(client, cabeceras_admin, cabeceras_profesor):
    crear = _crear_solicitud(client)
    assert crear.status_code == 201
    id_solicitud = crear.json()["id_solicitud"]
    assert crear.json()["postulante"] == "Test Alumno Solicitud"

    listar = client.get("/api/v1/comunidad/solicitudes", headers=cabeceras_admin)
    assert listar.status_code == 200
    assert any(s["id_solicitud"] == id_solicitud for s in listar.json())

    aprobar = client.put(
        f"/api/v1/comunidad/solicitudes/{id_solicitud}/estado",
        json={"estado": "Aprobado", "observaciones": "Documentación completa"},
        headers=cabeceras_admin,
    )
    assert aprobar.status_code == 200
    assert aprobar.json()["estado"] == "Aprobado"

    # El docente no puede ver ni moderar solicitudes
    assert client.get("/api/v1/comunidad/solicitudes", headers=cabeceras_profesor).status_code == 403
    assert (
        client.put(
            f"/api/v1/comunidad/solicitudes/{id_solicitud}/estado",
            json={"estado": "Rechazado"},
            headers=cabeceras_profesor,
        ).status_code
        == 403
    )


def test_solicitud_con_datos_invalidos_devuelve_422(client):
    respuesta = client.post(
        "/api/v1/comunidad/solicitudes",
        json={"postulante": "Ab", "dni": "1", "nivel": "x", "tutor": ""},
    )
    assert respuesta.status_code == 422


def test_mensaje_de_contacto_y_marcar_leido(client, cabeceras_admin):
    crear = client.post(
        "/api/v1/comunidad/contacto",
        json={
            "nombre": "Familia Test",
            "telefono": "3624000088",
            "correo": "familia.test@gmail.com",
            "mensaje": "Quisiera consultar por las vacantes de Sala de 4.",
        },
    )
    assert crear.status_code == 201
    id_mensaje = crear.json()["id_mensaje"]
    assert crear.json()["leido"] is False

    listar = client.get("/api/v1/comunidad/contacto", headers=cabeceras_admin)
    assert listar.status_code == 200
    assert any(m["id_mensaje"] == id_mensaje for m in listar.json())

    marcar = client.put(
        f"/api/v1/comunidad/contacto/{id_mensaje}/leido",
        headers=cabeceras_admin,
    )
    assert marcar.status_code == 200
    assert marcar.json()["leido"] is True


def test_opiniones_requieren_aprobacion_para_publicarse(client, cabeceras_admin, cabeceras_profesor):
    crear = client.post(
        "/api/v1/comunidad/opiniones",
        json={
            "nombre": "Opinión Test",
            "vinculo": "Madre de 2° Grado",
            "comentario": "La escuela acompañó muy bien a mi hija durante el año.",
            "estrellas": 5,
        },
    )
    assert crear.status_code == 201
    id_opinion = crear.json()["id_opinion"]
    assert crear.json()["aprobada"] is False

    # La lista pública no la muestra hasta aprobarla
    publicas = client.get("/api/v1/comunidad/opiniones")
    assert publicas.status_code == 200
    assert all(o["id_opinion"] != id_opinion for o in publicas.json())

    # Solo ADMIN ve las pendientes y puede moderarlas
    todas = client.get("/api/v1/comunidad/opiniones/todas", headers=cabeceras_admin)
    assert todas.status_code == 200
    assert any(o["id_opinion"] == id_opinion for o in todas.json())
    assert (
        client.put(
            f"/api/v1/comunidad/opiniones/{id_opinion}/aprobar",
            headers=cabeceras_profesor,
        ).status_code
        == 403
    )

    aprobar = client.put(
        f"/api/v1/comunidad/opiniones/{id_opinion}/aprobar",
        headers=cabeceras_admin,
    )
    assert aprobar.status_code == 200
    assert aprobar.json()["aprobada"] is True

    publicas = client.get("/api/v1/comunidad/opiniones")
    assert any(o["id_opinion"] == id_opinion for o in publicas.json())

    eliminar = client.delete(
        f"/api/v1/comunidad/opiniones/{id_opinion}",
        headers=cabeceras_admin,
    )
    assert eliminar.status_code == 200
    publicas = client.get("/api/v1/comunidad/opiniones")
    assert all(o["id_opinion"] != id_opinion for o in publicas.json())


def test_postulacion_laboral_publica_y_visible_para_admin(client, cabeceras_admin, cabeceras_profesor):
    crear = client.post(
        "/api/v1/comunidad/postulaciones",
        json={
            "nombre": "Postulante Test",
            "correo": "postulante.test@gmail.com",
            "telefono": "3624000077",
            "puesto": "Docente de Idioma Francés / Inglés",
            "area": "Departamento de Lenguas Extranjeras",
            "mensaje": "Cuento con 5 años de experiencia.",
        },
    )
    assert crear.status_code == 201
    id_postulacion = crear.json()["id_postulacion"]

    listar = client.get("/api/v1/comunidad/postulaciones", headers=cabeceras_admin)
    assert listar.status_code == 200
    assert any(p["id_postulacion"] == id_postulacion for p in listar.json())

    assert client.get("/api/v1/comunidad/postulaciones", headers=cabeceras_profesor).status_code == 403


def test_postulacion_espontanea_usa_puesto_por_defecto(client):
    respuesta = client.post(
        "/api/v1/comunidad/postulaciones",
        json={
            "nombre": "Espontáneo Test",
            "correo": "espontaneo.test@gmail.com",
            "area": "Educación Física",
        },
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["puesto"] == "Postulación espontánea"
