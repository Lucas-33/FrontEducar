import flet as ft

from frontend.app.api_client import api_client  # <-- ACÁ ESTÁ LA SOLUCIÓN
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    ONLINE_GREEN,
    TEAL_DARK,
    TEXT_COLOR,
)
from frontend.app.components.portal_layout import portal_layout


async def get_padre_facturas_view(page: ft.Page) -> ft.Container:
    lista_facturas = ft.Column(spacing=12)

    def crear_fila_factura(factura: dict):
        estado = factura.get("estado", "PENDIENTE")
        color_estado = ONLINE_GREEN if estado == "PAGADA" else BADGE_RED_TXT
        icono_estado = (
            ft.Icons.CHECK_CIRCLE if estado == "PAGADA" else ft.Icons.ERROR_OUTLINE
        )

        return ft.Container(
            bgcolor=BG_WHITE,
            padding=16,
            border_radius=8,
            border=ft.Border.all(1, BORDER_COLOR),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=16,
                        controls=[
                            ft.Icon(icono_estado, color=color_estado, size=28),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        f"Período {factura.get('mes')}/{factura.get('anio')} - {factura.get('alumno_nombre')}",
                                        weight=ft.FontWeight.W_600,
                                        size=14,
                                        color=TEXT_COLOR,
                                    ),
                                    ft.Text(
                                        f"Vto: {factura.get('fecha_vencimiento')}",
                                        size=12,
                                        color=MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=2,
                        controls=[
                            ft.Text(
                                f"$ {factura.get('total', 0):.2f}",
                                weight=ft.FontWeight.BOLD,
                                size=15,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                estado,
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=color_estado,
                            ),
                        ],
                    ),
                ],
            ),
        )

    async def cargar_datos():
        try:
            # Llamada al cliente API (ahora sí está importado)
            facturas_reales = await api_client.get_mis_facturas()

            filas = [crear_fila_factura(f) for f in facturas_reales]
            lista_facturas.controls = (
                filas
                if filas
                else [ft.Text("No hay facturas registradas.", color=MUTED)]
            )
        except Exception as e:
            # Si el backend todavía no tiene el endpoint, caerá acá sin romper la app
            lista_facturas.controls = [
                ft.Text(
                    f"Esperando conexión con la base de datos... ({e})",
                    color=BADGE_RED_TXT,
                )
            ]
        page.update()

    page.run_task(cargar_datos)

    return portal_layout(
        page=page,
        titulo="Mis Facturas",
        active_route="/portal/padre/facturas",
        rol="Padre",
        content_controls=[
            ft.Text(
                "Historial de Facturación",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            lista_facturas,
        ],
    )
