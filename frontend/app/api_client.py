import httpx
from typing import Any, Optional


class APIClient:
    """Cliente HTTP asíncrono centralizado para interactuar con la API REST de FastAPI."""

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
        self._client: Optional[httpx.AsyncClient] = None
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

    # ==================== AUTENTICACIÓN ====================
    async def login(self, username: str, password: str) -> dict[str, Any]:
        client = self._get_client()
        url = f"{self.base_url}/auth/login"
        payload = {"username": username, "password": password}

        response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()

        data = response.json()
        if "access_token" in data:
            self.set_token(data["access_token"])
        return data

    # ==================== ALUMNOS ====================
    async def get_alumnos(self, solo_activos: bool = True) -> list[dict[str, Any]]:
        client = self._get_client()
        url = f"{self.base_url}/personas/alumnos"
        params = {"solo_activos": str(solo_activos).lower()}

        response = await client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    async def create_alumno(self, data: dict[str, Any]) -> dict[str, Any]:
        client = self._get_client()
        url = f"{self.base_url}/personas/alumnos"
        response = await client.post(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    async def update_alumno(self, legajo: str, data: dict[str, Any]) -> dict[str, Any]:
        client = self._get_client()
        url = f"{self.base_url}/personas/alumnos/{legajo}"
        response = await client.put(url, json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    async def delete_alumno(self, legajo: str) -> bool:
        client = self._get_client()
        url = f"{self.base_url}/personas/alumnos/{legajo}"
        response = await client.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return True

    # ==================== ACADÉMICO / CURSOS ====================
    async def get_cursos(self) -> list[dict[str, Any]]:
        client = self._get_client()
        url = f"{self.base_url}/academico/cursos"
        response = await client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()


api_client = APIClient()