import os
from typing import Any, Optional

import httpx


class MobileAPIClient:
    """Cliente HTTP asíncrono para la aplicación móvil de Educar para Transformar."""

    _instance: Optional["MobileAPIClient"] = None

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

    def set_base_url(self, url: str) -> None:
        """Permite cambiar la IP del backend (vital para pruebas en teléfono físico vía WiFi)."""
        clean_url = url.strip().rstrip("/")
        if not clean_url.endswith("/api/v1"):
            clean_url = f"{clean_url}/api/v1"
        self.base_url = clean_url

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=12.0)
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

    # ==================== FAMILIAS, FACTURAS Y PAGOS ====================
    async def get_mis_facturas(self) -> list[dict[str, Any]]:
        return await self._get("/finanzas/mis-facturas")

    async def post_comprobante(
        self, id_factura: int, archivo_url: str
    ) -> dict[str, Any]:
        payload = {"id_factura": id_factura, "archivo_url": archivo_url}
        return await self._post("/finanzas/comprobantes", data=payload)

    async def get_hijos(self, id_padre: int) -> list[dict[str, Any]]:
        return await self._get(f"/personas/padres/{id_padre}/alumnos")

    # ==================== SERVICIOS: DEPORTES ====================
    async def get_deportes(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/deportes")

    async def get_grupos_deporte(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/deportes/grupos")

    async def get_inscripciones_deporte(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/deportes/inscripciones")

    async def inscribir_deporte(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/deportes/inscripciones", data=data)

    # ==================== SERVICIOS: TRANSPORTE Y COMEDOR ====================
    async def get_recorridos_transporte(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/transporte/recorridos")

    async def get_inscripciones_transporte(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/transporte/inscripciones")

    async def inscribir_transporte(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/transporte/inscripciones", data=data)

    async def baja_transporte(self, legajo_alumno: int) -> dict[str, Any]:
        return await self._delete(
            f"/servicios/transporte/inscripciones/{legajo_alumno}"
        )

    async def get_inscripciones_comedor(self) -> list[dict[str, Any]]:
        return await self._get("/servicios/comedor/inscripciones")

    async def inscribir_comedor(self, data: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/servicios/comedor/inscripciones", data=data)

    async def baja_comedor(self, legajo_alumno: int) -> dict[str, Any]:
        return await self._delete(f"/servicios/comedor/inscripciones/{legajo_alumno}")


mobile_api = MobileAPIClient()
