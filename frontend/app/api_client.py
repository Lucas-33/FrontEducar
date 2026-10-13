import httpx
from typing import Any, Optional


class APIClient:
    """Cliente HTTP centralizado para interactuar con la API REST de FastAPI."""

    _instance: Optional["APIClient"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1"):
        if getattr(self, "_initialized", False):
            return

        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self._client = httpx.Client(timeout=10.0)
        self._initialized = True

    def set_token(self, token: str) -> None:
        """Establece el token JWT en memoria para las peticiones subsecuentes."""
        self.token = token

    def clear_token(self) -> None:
        """Elimina el token JWT activo."""
        self.token = None

    def _get_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ==================== AUTENTICACIÓN ====================
    def login(self, username: str, password: str) -> dict[str, Any]:
        """
        POST /api/v1/auth/login
        Retorna: {access_token, token_type, rol, username}
        """
        url = f"{self.base_url}/auth/login"
        payload = {"username": username, "password": password}

        response = self._client.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()

        data = response.json()
        if "access_token" in data:
            self.set_token(data["access_token"])
        return data

    # ==================== ALUMNOS ====================
    def get_alumnos(self, solo_activos: bool = True) -> list[dict[str, Any]]:
        """
        GET /api/v1/personas/alumnos?solo_activos=true
        Retorna la lista de estudiantes.
        """
        url = f"{self.base_url}/personas/alumnos"
        params = {"solo_activos": str(solo_activos).lower()}

        response = self._client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def create_alumno(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        POST /api/v1/personas/alumnos
        Crea un nuevo alumno en la base de datos.
        """
        url = f"{self.base_url}/personas/alumnos"
        response = self._client.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def update_alumno(self, legajo: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        PUT /api/v1/personas/alumnos/{legajo}
        Actualiza los datos del estudiante.
        """
        url = f"{self.base_url}/personas/alumnos/{legajo}"
        response = self._client.put(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def delete_alumno(self, legajo: str) -> bool:
        """
        DELETE /api/v1/personas/alumnos/{legajo}
        Baja lógica del alumno.
        """
        url = f"{self.base_url}/personas/alumnos/{legajo}"
        response = self._client.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return True

    # ==================== ACADÉMICO / CURSOS ====================
    def get_cursos(self) -> list[dict[str, Any]]:
        """
        GET /api/v1/academico/cursos
        Retorna los cursos y divisiones disponibles.
        """
        url = f"{self.base_url}/academico/cursos"
        response = self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()


# Instancia singleton lista para usar en los módulos de interfaz
api_client = APIClient()