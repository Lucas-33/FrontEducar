"""Tests de los servicios escolares (Deportes, Transporte, Comedor)."""
from backend.tests.conftest import LEGAJO_ALUMNO_1


def test_limite_deportes_y_conflictos_horario(client, cabeceras_admin):
    # 1. Crear turnos/horarios de prueba
    h1 = client.post(
        "/api/v1/academico/horarios",
        json={"descripcion": "Turno Mañana"},
        headers=cabeceras_admin,
    ).json()["id_horario"]
    h2 = client.post(
        "/api/v1/academico/horarios",
        json={"descripcion": "Turno Tarde"},
        headers=cabeceras_admin,
    ).json()["id_horario"]

    # 2. Crear deportes
    d_futbol = client.post(
        "/api/v1/servicios/deportes", json={"nombre": "Fútbol"}, headers=cabeceras_admin
    ).json()["id_deporte"]
    d_voley = client.post(
        "/api/v1/servicios/deportes", json={"nombre": "Vóley"}, headers=cabeceras_admin
    ).json()["id_deporte"]
    d_basquet = client.post(
        "/api/v1/servicios/deportes",
        json={"nombre": "Básquet"},
        headers=cabeceras_admin,
    ).json()["id_deporte"]

    # 3. Crear grupos deportivos (id_nivel=1 ya existe gracias a conftest.py)
    # Grupo 1: Fútbol a la Mañana
    g_futbol_manana = client.post(
        "/api/v1/servicios/deportes/grupos",
        json={"id_deporte": d_futbol, "id_nivel": 1, "id_horario": h1},
        headers=cabeceras_admin,
    ).json()["id_grupo"]

    # Grupo 2: Vóley a la Tarde
    g_voley_tarde = client.post(
        "/api/v1/servicios/deportes/grupos",
        json={"id_deporte": d_voley, "id_nivel": 1, "id_horario": h2},
        headers=cabeceras_admin,
    ).json()["id_grupo"]

    # Grupo 3: Básquet a la Mañana (¡Mismo horario que Fútbol!)
    g_basquet_manana = client.post(
        "/api/v1/servicios/deportes/grupos",
        json={"id_deporte": d_basquet, "id_nivel": 1, "id_horario": h1},
        headers=cabeceras_admin,
    ).json()["id_grupo"]

    # Grupo 4: Básquet a la Tarde (Diferente horario)
    g_basquet_tarde = client.post(
        "/api/v1/servicios/deportes/grupos",
        json={"id_deporte": d_basquet, "id_nivel": 1, "id_horario": h2},
        headers=cabeceras_admin,
    ).json()["id_grupo"]

    # 4. Inscribir al primer deporte (Fútbol a la Mañana) -> DEBE FUNCIONAR (201)
    resp1 = client.post(
        "/api/v1/servicios/deportes/inscripciones",
        json={"legajo_alumno": LEGAJO_ALUMNO_1, "id_grupo": g_futbol_manana},
        headers=cabeceras_admin,
    )
    assert resp1.status_code == 201

    # 5. Inscribir a Básquet a la Mañana -> DEBE FALLAR POR CONFLICTO DE HORARIO (409)
    resp2 = client.post(
        "/api/v1/servicios/deportes/inscripciones",
        json={"legajo_alumno": LEGAJO_ALUMNO_1, "id_grupo": g_basquet_manana},
        headers=cabeceras_admin,
    )
    assert resp2.status_code == 409
    assert "conflicto de horarios" in resp2.json()["detail"].lower()

    # 6. Inscribir a Vóley a la Tarde -> DEBE FUNCIONAR (201)
    resp3 = client.post(
        "/api/v1/servicios/deportes/inscripciones",
        json={"legajo_alumno": LEGAJO_ALUMNO_1, "id_grupo": g_voley_tarde},
        headers=cabeceras_admin,
    )
    assert resp3.status_code == 201

    # 7. Inscribir a un TERCER deporte (Básquet a la Tarde) -> DEBE FALLAR POR LÍMITE ALCANZADO (400)
    resp4 = client.post(
        "/api/v1/servicios/deportes/inscripciones",
        json={"legajo_alumno": LEGAJO_ALUMNO_1, "id_grupo": g_basquet_tarde},
        headers=cabeceras_admin,
    )
    assert resp4.status_code == 400
    assert "límite máximo" in resp4.json()["detail"].lower()
