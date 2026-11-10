import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.portal_layout import portal_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)


async def get_padre_facturas_view(page: ft.Page) -> ft.Container:
    lista_facturas = ft.Column(spacing=12)
    factura_seleccionada = None

    # ==================== MODAL DE PAGO ====================
    input_archivo = ft.TextField(
        label="Nombre del archivo",
        value="comprobante_transferencia.pdf",
        expand=True,
        text_size=14,
    )

    def cerrar_dialogo(_=None):
        dialogo_pago.open = False
        page.update()

    async def enviar_comprobante(e):
        if not factura_seleccionada:
            return

        try:
            btn_enviar.disabled = True
            page.update()

            # Llamada al backend (usamos el endpoint que creamos)
            await api_client.post_comprobante(
                id_factura=factura_seleccionada["id"], archivo_url=input_archivo.value
            )

            cerrar_dialogo()

            # MAGIA: Usamos page.overlay para que la alerta verde no quede escondida
            alerta_exito = ft.SnackBar(
                ft.Text(
                    "¡Comprobante enviado! Pendiente de aprobación.", color=BG_WHITE
                ),
                bgcolor=ONLINE_GREEN,
            )
            page.overlay.append(alerta_exito)
            alerta_exito.open = True

            await cargar_datos()

        except Exception as ex:
            alerta_error = ft.SnackBar(
                ft.Text(f"Error al enviar: {ex}", color=BG_WHITE), bgcolor=BADGE_RED_TXT
            )
            page.overlay.append(alerta_error)
            alerta_error.open = True
        finally:
            btn_enviar.disabled = False
            page.update()

    btn_enviar = ft.ElevatedButton(
        "Enviar a Administración",
        bgcolor=TEAL,
        color=BG_WHITE,
        on_click=enviar_comprobante,
    )

    dialogo_pago = ft.AlertDialog(
        title=ft.Text(
            "Informar Pago", color=TEAL_DARK, weight=ft.FontWeight.BOLD, size=18
        ),
        content=ft.Column(
            tight=True,
            spacing=16,
            controls=[
                ft.Text(
                    "Adjuntá el comprobante de transferencia o depósito bancario para validar tu pago.",
                    size=13,
                    color=TEXT_COLOR,
                ),
                ft.Row(
                    controls=[ft.Icon(ft.Icons.ATTACH_FILE, color=TEAL), input_archivo]
                ),
            ],
        ),
        actions=[ft.TextButton("Cancelar", on_click=cerrar_dialogo), btn_enviar],
    )

    def abrir_dialogo_pago(factura):
        nonlocal factura_seleccionada
        factura_seleccionada = factura

        # MAGIA: Agregamos el modal a la capa flotante superior para que la "Vista" actual no lo tape
        if dialogo_pago not in page.overlay:
            page.overlay.append(dialogo_pago)

        dialogo_pago.open = True
        page.update()

    # ==================== INTERFAZ DE FACTURAS ====================
    def crear_fila_factura(factura: dict):
        estado = factura.get("estado", "PENDIENTE")
        color_estado = ONLINE_GREEN if estado == "PAGADA" else BADGE_RED_TXT
        icono_estado = (
            ft.Icons.CHECK_CIRCLE if estado == "PAGADA" else ft.Icons.ERROR_OUTLINE
        )

        fila_datos = ft.Row(
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
        )

        controles_tarjeta = [fila_datos]

        if estado == "PENDIENTE":
            boton_pagar = ft.Container(
                margin=ft.Margin(top=12, right=0, bottom=0, left=0),
                content=ft.OutlinedButton(
                    "Informar Pago",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _: abrir_dialogo_pago(factura),
                    style=ft.ButtonStyle(
                        color=TEAL,
                        side=ft.BorderSide(1, TEAL),
                        shape=ft.RoundedRectangleBorder(radius=6),
                    ),
                    height=36,
                ),
            )
            controles_tarjeta.append(boton_pagar)

        return ft.Container(
            bgcolor=BG_WHITE,
            padding=16,
            border_radius=8,
            border=ft.Border.all(1, BORDER_COLOR),
            content=ft.Column(spacing=0, controls=controles_tarjeta),
        )

    async def cargar_datos():
        try:
            facturas_reales = await api_client.get_mis_facturas()
            filas = [crear_fila_factura(f) for f in facturas_reales]
            lista_facturas.controls = (
                filas
                if filas
                else [ft.Text("No hay facturas registradas.", color=MUTED)]
            )
        except Exception as e:
            lista_facturas.controls = [
                ft.Text(f"Error de conexión: {e}", color=BADGE_RED_TXT)
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
