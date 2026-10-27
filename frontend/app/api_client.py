import os
from typing import Any, Optional

import httpx


class APIClient:
    """Cliente HTTP asíncrono centralizado para interactuar con la API REST de FastAPI.

    La URL base se puede configurar con la variable de entorno API_BASE_URL
    (por defecto http://127.0.0.1:8000/api/v1) para poder desplegar el sistema
    en otro servidor sin tocar el código.
    """

    _instance: Optional["APIClient"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_url: str | None = None):
        if getattr(self, "_initialized", False):
            return

        self.base_url = (
            base_url or os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
        ).rstrip("/")
        self.token: str | None = None
        self._client: httpx.AsyncClient | None = None
        self._initialized = True

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    def set_token(self, token: str) -> None:
        self.token = token

    def clear_token(self) -> None:
        self.token = None

    def _get_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ==================== HELPERS INTERNOS ====================
    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        client = self._get_client()
        response = await client.get(
            f"{self.base_url}{path}", params=params, headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, data: dict[str, Any]) -> Any:
        client = self._get_client()
        response = await client.post(
            f"{self.base_url}{path}", json=data, headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    async def _put(self, path: str, data: dict[str, Any]) -> Any:
        client = self._get_client()
        response = await client.put(
            f"{self.base_url}{path}", json=data, headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    async def _delete(self, path: str) -> Any:
        client = self._get_client()
        response = await client.delete(
            f"{self.base_url}{path}", headers=self._get_headers()
        )
        response.raise_for_status()
        if response.content:
            return response.json()
        return None

    # ==================== AUTENTICACIÓN ====================
    async def login(self, username: str, password: str) -> dict[str, Any]:
        client = self._get_client()
        url = f"{self.base_url}/auth/login"
        payload = {"username": username, "password": password}

        response = await client.post(
            url, json=payload, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        data = response.json()
        if "access_token" in data:
            self.set_token(data["access_token"])
        return data

    async def get_mi_perfil(self) -> dict[str, Any]:
        return await self._get("/auth/me")

    async def cambiar_password(
        self, password_actual: str, password_nueva: str
    ) -> dict[str, Any]:
        return await self._put(
            "/auth/me/password",
            {"password_actual": password_actual, "password_nueva": password_nueva},
        )

    # ==================== USUARIOS Y ROLES ====================
    async def get_usuarios(self) -> list[dict[str, Any]]:
        return await self._get("/auth/usuarios")

    async def get_roles(self) -> list[dict[str, Any]]:
        return await self._get("/auth/roles")

    async def create_usuario(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/auth/usuarios", data)

    async def update_usuario(
        self, id_usuario: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/auth/usuarios/{id_usuario}", data)

    # ==================== ALUMNOS ====================
    async def get_alumnos(
        self,
        solo_activos: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        client = self._get_client()
        url = f"{self.base_url}/personas/alumnos"
        params = {
            "solo_activos": str(solo_activos).lower(),
            "skip": skip,
            "limit": limit,
        }

        response = await client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    async def get_todos_los_alumnos(
        self, solo_activos: bool = False
    ) -> list[dict[str, Any]]:
        """Recorre todas las páginas del listado para no perder alumnos."""
        alumnos: list[dict[str, Any]] = []
        tamano_pagina = 100
        skip = 0
        while True:
            pagina = await self.get_alumnos(
                solo_activos=solo_activos,
                skip=skip,
                limit=tamano_pagina,
            )
            alumnos.extend(pagina)
            if len(pagina) < tamano_pagina:
                break
            skip += tamano_pagina
        return alumnos

    async def get_alumno(self, legajo: int) -> dict[str, Any]:
        return await self._get(f"/personas/alumnos/{legajo}")

    async def create_alumno(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/personas/alumnos", data)

    async def update_alumno(self, legajo: int, data: dict[str, Any]) -> dict[str, Any]:
        return await self._put(f"/personas/alumnos/{legajo}", data)

    async def delete_alumno(self, legajo: int) -> dict[str, Any]:
        return await self._delete(f"/personas/alumnos/{legajo}")

    # ==================== PROFESORES ====================
    async def get_profesores(self, solo_activos: bool = True) -> list[dict[str, Any]]:
        client = self._get_client()
        url = f"{self.base_url}/personas/profesores"
        params = {"solo_activos": str(solo_activos).lower(), "limit": 100}

        response = await client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    async def create_profesor(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/personas/profesores", data)

    async def update_profesor(
        self, legajo: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/personas/profesores/{legajo}", data)

    async def delete_profesor(self, legajo: int) -> dict[str, Any]:
        return await self._delete(f"/personas/profesores/{legajo}")

    # ==================== PADRES / TUTORES ====================
    async def get_padres(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        return await self._get(
            "/personas/padres", params={"skip": skip, "limit": limit}
        )

    async def get_todos_los_padres(self) -> list[dict[str, Any]]:
        """Recorre todas las páginas del listado de tutores."""
        padres: list[dict[str, Any]] = []
        tamano_pagina = 100
        skip = 0
        while True:
            pagina = await self.get_padres(skip=skip, limit=tamano_pagina)
            padres.extend(pagina)
            if len(pagina) < tamano_pagina:
                break
            skip += tamano_pagina
        return padres

    async def get_hijos(self, id_padre: int) -> list[dict[str, Any]]:
        return await self._get(f"/personas/padres/{id_padre}/alumnos")

    async def create_padre(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/personas/padres", data)

    # ==================== NIVELES EDUCATIVOS ====================
    async def get_niveles(self) -> list[dict[str, Any]]:
        return await self._get("/academico/niveles")

    async def create_nivel(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/academico/niveles", data)

    async def update_nivel(self, id_nivel: int, data: dict[str, Any]) -> dict[str, Any]:
        return await self._put(f"/academico/niveles/{id_nivel}", data)

    async def delete_nivel(self, id_nivel: int) -> dict[str, Any]:
        return await self._delete(f"/academico/niveles/{id_nivel}")

    # ==================== CURSOS ====================
    async def get_cursos(self, id_nivel: int | None = None) -> list[dict[str, Any]]:
        params = {"id_nivel": id_nivel} if id_nivel is not None else None
        return await self._get("/academico/cursos", params=params)

    async def create_curso(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/academico/cursos", data)

    async def update_curso(self, id_curso: int, data: dict[str, Any]) -> dict[str, Any]:
        return await self._put(f"/academico/cursos/{id_curso}", data)

    async def delete_curso(self, id_curso: int) -> dict[str, Any]:
        return await self._delete(f"/academico/cursos/{id_curso}")

    # ==================== MATERIAS ====================
    async def get_materias(self) -> list[dict[str, Any]]:
        return await self._get("/academico/materias")

    async def create_materia(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/academico/materias", data)

    async def update_materia(
        self, id_materia: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/academico/materias/{id_materia}", data)

    async def delete_materia(self, id_materia: int) -> dict[str, Any]:
        return await self._delete(f"/academico/materias/{id_materia}")

    # ==================== ASIGNACIONES (materia-curso-profesor) ====================
    async def get_asignaciones(self) -> list[dict[str, Any]]:
        return await self._get("/academico/asignaciones")

    async def create_asignacion(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/academico/asignaciones", data)

    async def update_asignacion(
        self, id_materia: int, id_curso: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/academico/asignaciones/{id_materia}/{id_curso}", data)

    async def delete_asignacion(self, id_materia: int, id_curso: int) -> dict[str, Any]:
        return await self._delete(f"/academico/asignaciones/{id_materia}/{id_curso}")

    # ==================== HORARIOS ====================
    async def get_horarios(self) -> list[dict[str, Any]]:
        return await self._get("/academico/horarios")

    async def create_horario(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/academico/horarios", data)

    async def update_horario(
        self, id_horario: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/academico/horarios/{id_horario}", data)

    async def delete_horario(self, id_horario: int) -> dict[str, Any]:
        return await self._delete(f"/academico/horarios/{id_horario}")

    # ==================== CALIFICACIONES (notas) ====================
    async def get_calificaciones(
        self,
        legajo_alumno: int | None = None,
        id_materia: int | None = None,
        id_curso: int | None = None,
        periodo: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if legajo_alumno is not None:
            params["legajo_alumno"] = legajo_alumno
        if id_materia is not None:
            params["id_materia"] = id_materia
        if id_curso is not None:
            params["id_curso"] = id_curso
        if periodo:
            params["periodo"] = periodo
        return await self._get("/academico/calificaciones", params=params or None)

    async def crear_calificacion(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/academico/calificaciones", data)

    async def actualizar_calificacion(
        self, id_calificacion: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/academico/calificaciones/{id_calificacion}", data)

    async def eliminar_calificacion(self, id_calificacion: int) -> dict[str, Any]:
        return await self._delete(f"/academico/calificaciones/{id_calificacion}")

    # ==================== ASISTENCIA ====================
    async def get_asistencia(
        self,
        id_curso: int | None = None,
        fecha: str | None = None,
        legajo_alumno: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if id_curso is not None:
            params["id_curso"] = id_curso
        if fecha:
            params["fecha"] = fecha
        if legajo_alumno is not None:
            params["legajo_alumno"] = legajo_alumno
        return await self._get("/academico/asistencia", params=params or None)

    async def registrar_asistencia_lote(
        self, data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        return await self._post("/academico/asistencia/lote", data)

    async def get_resumen_asistencia(self, legajo_alumno: int) -> dict[str, Any]:
        return await self._get(f"/academico/asistencia/resumen/{legajo_alumno}")

    async def eliminar_asistencia(self, id_asistencia: int) -> dict[str, Any]:
        return await self._delete(f"/academico/asistencia/{id_asistencia}")

    # ==================== DEPORTES ====================
    async def get_deportes(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/deportes")

    async def create_deporte(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/deportes", data)

    async def update_deporte(
        self, id_deporte: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/servicios/deportes/{id_deporte}", data)

    async def delete_deporte(self, id_deporte: int) -> dict[str, Any]:
        return await self._delete(f"/servicios/deportes/{id_deporte}")

    async def get_grupos_deporte(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/deportes/grupos")

    async def create_grupo_deporte(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/deportes/grupos", data)

    async def update_grupo_deporte(
        self, id_grupo: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/servicios/deportes/grupos/{id_grupo}", data)

    async def delete_grupo_deporte(self, id_grupo: int) -> dict[str, Any]:
        return await self._delete(f"/servicios/deportes/grupos/{id_grupo}")

    async def get_inscripciones_deporte(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/deportes/inscripciones")

    async def inscribir_deporte(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/deportes/inscripciones", data)

    # ==================== TRANSPORTE ====================
    async def get_recorridos(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/transporte/recorridos")

    async def create_recorrido(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/transporte/recorridos", data)

    async def update_recorrido(
        self, id_recorrido: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        return await self._put(f"/servicios/transporte/recorridos/{id_recorrido}", data)

    async def delete_recorrido(self, id_recorrido: int) -> dict[str, Any]:
        return await self._delete(f"/servicios/transporte/recorridos/{id_recorrido}")

    async def get_inscripciones_transporte(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/transporte/inscripciones")

    async def inscribir_transporte(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/transporte/inscripciones", data)

    async def baja_transporte(self, legajo_alumno: int) -> dict[str, Any]:
        return await self._delete(
            f"/servicios/transporte/inscripciones/{legajo_alumno}"
        )

    # ==================== COMEDOR ====================
    async def get_inscripciones_comedor(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/comedor/inscripciones")

    async def inscribir_comedor(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/comedor/inscripciones", data)

    async def baja_comedor(self, legajo_alumno: int) -> dict[str, Any]:
        return await self._delete(f"/servicios/comedor/inscripciones/{legajo_alumno}")

    # ==================== COMUNIDAD (admisiones, contacto, opiniones, empleo) ====================
    async def crear_solicitud(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/comunidad/solicitudes", data)

    async def get_solicitudes(self) -> list[dict[str, Any]]:
        return await self._get("/comunidad/solicitudes")

    async def cambiar_estado_solicitud(
        self, id_solicitud: int, estado: str, observaciones: str | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"estado": estado}
        if observaciones is not None:
            payload["observaciones"] = observaciones
        return await self._put(f"/comunidad/solicitudes/{id_solicitud}/estado", payload)

    async def enviar_contacto(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/comunidad/contacto", data)

    async def get_mensajes_contacto(self) -> list[dict[str, Any]]:
        return await self._get("/comunidad/contacto")

    async def marcar_mensaje_leido(self, id_mensaje: int) -> dict[str, Any]:
        return await self._put(f"/comunidad/contacto/{id_mensaje}/leido", {})

    async def crear_opinion(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/comunidad/opiniones", data)

    async def get_opiniones(self) -> list[dict[str, Any]]:
        return await self._get("/comunidad/opiniones")

    async def get_opiniones_todas(self) -> list[dict[str, Any]]:
        return await self._get("/comunidad/opiniones/todas")

    async def aprobar_opinion(self, id_opinion: int) -> dict[str, Any]:
        return await self._put(f"/comunidad/opiniones/{id_opinion}/aprobar", {})

    async def eliminar_opinion(self, id_opinion: int) -> dict[str, Any]:
        return await self._delete(f"/comunidad/opiniones/{id_opinion}")

    async def enviar_postulacion(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/comunidad/postulaciones", data)

    async def get_postulaciones(self) -> list[dict[str, Any]]:
        return await self._get("/comunidad/postulaciones")

    # ==================== DASHBOARD ====================
    async def get_resumen_dashboard(self) -> dict[str, Any]:
        return await self._get("/dashboard/resumen")

    # ==================== REPORTES EXCEL ====================
    def reporte_url(self, nombre: str) -> str:
        """URL absoluta de descarga de un reporte Excel, con el token de sesión."""
        return f"{self.base_url}/reportes/{nombre}.xlsx?token={self.token or ''}"


api_client = APIClient()
