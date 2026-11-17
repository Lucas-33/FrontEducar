import flet as ft
import httpx

from app.api_client import api_client
from app.components.admin_layout import admin_layout
from app.components.constants import (
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_TXT,
    BADGE_YELLOW_BG,
    BADGE_YELLOW_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


async def get_admin_finanzas_view(page: ft.Page) -> ft.Row:
    """Pantalla para que el Administrador configure los precios del sistema."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    aviso = ft.Text("", size=13, weight=ft.FontWeight.W_600, visible=False)

    def mostrar_mensaje(texto: str, es_error: bool = False):
        aviso.value = texto
        aviso.color = BADGE_RED_TXT if es_error else ONLINE_GREEN
        aviso.visible = True
        page.update()

    def campo_precio(label: str, valor_inicial: str = "0.00") -> ft.TextField:
        return ft.TextField(
            label=label,
            value=valor_inicial,
            prefix=ft.Text("$ ", color=TEXT_COLOR),
            text_size=14,
            color=TEXT_COLOR,  # <--- FUENTE NEGRA / OSCURA DENTRO DEL INPUT
            width=280,
            height=CONTROL_HEIGHT,
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            border_radius=BORDER_RADIUS,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$"),
        )

    # ==================== 1. VALORES INSTITUCIONALES FIJOS ====================
    input_cuota = campo_precio("Valor de la Cuota Base Mensual")
    input_comedor = campo_precio("Valor Mensual del Comedor")

    async def guardar_fijos(e):
        try:
            val_cuota = float(input_cuota.value or 0)
            val_comedor = float(input_comedor.value or 0)
            await api_client.update_configuracion("CUOTA_BASE", val_cuota)
            await api_client.update_configuracion("COMEDOR", val_comedor)
            mostrar_mensaje("Valores institucionales actualizados correctamente.")
        except Exception as err:
            mostrar_mensaje(f"Error al guardar: {err}", es_error=True)

    card_fijos = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    "Cuota Base y Comedor",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.Text(
                    "Estos valores impactarán en la facturación del próximo mes para todos los inscriptos.",
                    size=13,
                    color=MUTED,
                ),
                ft.Row(spacing=16, controls=[input_cuota, input_comedor]),
                ft.Button(
                    "Guardar Valores Fijos",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=guardar_fijos,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                    ),
                ),
            ],
        ),
    )

    # ==================== 2. VALORES DE DEPORTES ====================
    lista_deportes = ft.Column(spacing=12)

    async def cargar_datos():
        # --- 1. Cargar Precios Fijos ---
        try:
            cuota_data = await api_client.get_configuracion("CUOTA_BASE")
            comedor_data = await api_client.get_configuracion("COMEDOR")

            input_cuota.value = str(cuota_data.get("valor", "0.00"))
            input_comedor.value = str(comedor_data.get("valor", "0.00"))
        except Exception:
            pass

        # --- 2. Cargar Deportes ---
        try:
            deportes = await api_client.get_deportes()
            filas = []
            inputs_deportes = []  # Guardamos las referencias para procesarlas todas juntas

            for d in deportes:
                input_precio = campo_precio(
                    f"Precio: {d['nombre']}", str(d.get("precio_mensual", 0))
                )
                inputs_deportes.append(
                    {
                        "id_deporte": d["id_deporte"],
                        "nombre": d["nombre"],
                        "input": input_precio,
                    }
                )

                filas.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                d["nombre"],
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=TEXT_COLOR,
                                width=200,
                            ),
                            input_precio,
                            # Eliminamos el botón individual de cada fila
                        ],
                    )
                )

            if filas:
                # Botón global para guardar todos los deportes a la vez
                async def guardar_todos_deportes(e):
                    errores = 0
                    for item in inputs_deportes:
                        try:
                            await api_client.update_deporte(
                                item["id_deporte"],
                                {
                                    "nombre": item["nombre"],
                                    "precio_mensual": float(item["input"].value or 0),
                                },
                            )
                        except Exception:
                            errores += 1

                    if errores == 0:
                        mostrar_mensaje(
                            "Todos los precios deportivos se actualizaron correctamente."
                        )
                    else:
                        mostrar_mensaje(
                            f"Se guardó parcialmente: hubo {errores} errores.",
                            es_error=True,
                        )

                btn_guardar_deportes = ft.Button(
                    "Guardar Precios Deportivos",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=guardar_todos_deportes,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                    ),
                )

                filas.append(ft.Container(height=8))  # Un pequeño espacio
                filas.append(
                    btn_guardar_deportes
                )  # Agregamos el botón al final de la lista

            lista_deportes.controls = filas or [
                ft.Text("No hay deportes registrados.", color=MUTED)
            ]
        except Exception:
            lista_deportes.controls = [
                ft.Text("Error al cargar deportes.", color=BADGE_RED_TXT)
            ]

        # --- 3. Cargar Comprobantes en Revisión ---
        await cargar_comprobantes()

        # --- 4. Refrescar UI ---
        page.update()

    # ==================== 3. BANDEJA DE VALIDACIÓN DE COMPROBANTES ====================
    badge_comprobantes = ft.Container(
        padding=ft.Padding(10, 4, 10, 4),
        border_radius=12,
        bgcolor=TEAL_LIGHT,
        content=ft.Text(
            "0 pendientes", size=12, weight=ft.FontWeight.BOLD, color=TEAL_DARK
        ),
    )
    lista_comprobantes_holder = ft.Column(spacing=12)

    def cerrar_dlg(dialogo):
        dialogo.open = False
        page.update()

    async def ejecutar_aprobar(id_comp: int, dialogo: ft.AlertDialog):
        try:
            res = await api_client.aprobar_comprobante(id_comp)
            cerrar_dlg(dialogo)
            mostrar_mensaje(
                f"✓ {res.get('mensaje', 'Comprobante aprobado exitosamente. Factura cancelada.')}"
            )
            await cargar_comprobantes()
        except Exception as ex:
            cerrar_dlg(dialogo)
            mostrar_mensaje(f"Error al aprobar comprobante: {ex}", es_error=True)

    async def ejecutar_rechazar(id_comp: int, dialogo: ft.AlertDialog):
        try:
            res = await api_client.rechazar_comprobante(id_comp)
            cerrar_dlg(dialogo)
            mostrar_mensaje(
                f"{res.get('mensaje', 'Comprobante rechazado. La factura permanece pendiente.')}",
                es_error=True,
            )
            await cargar_comprobantes()
        except Exception as ex:
            cerrar_dlg(dialogo)
            mostrar_mensaje(f"Error al rechazar comprobante: {ex}", es_error=True)

    async def cargar_comprobantes():
        try:
            comprobantes = await api_client.get_comprobantes_pendientes()
            cant = len(comprobantes)
            if cant > 0:
                badge_comprobantes.bgcolor = BADGE_YELLOW_BG
                badge_comprobantes.content.color = BADGE_YELLOW_TXT
                badge_comprobantes.content.value = (
                    f"{cant} en revisión{'s' if cant > 1 else ''}"
                )
            else:
                badge_comprobantes.bgcolor = BADGE_GREEN_BG
                badge_comprobantes.content.color = BADGE_GREEN_TXT
                badge_comprobantes.content.value = "0 pendientes · Al día"

            if not comprobantes:
                lista_comprobantes_holder.controls = [
                    ft.Container(
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=BORDER_RADIUS,
                        padding=28,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=12,
                            controls=[
                                ft.Icon(
                                    ft.Icons.VERIFIED_OUTLINED,
                                    color=ONLINE_GREEN,
                                    size=24,
                                ),
                                ft.Text(
                                    "No hay comprobantes pendientes de revisión. Todos los pagos informados están al día.",
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=TEXT_COLOR,
                                ),
                            ],
                        ),
                    )
                ]
                page.update()
                return

            filas_tabla = []
            for comp in comprobantes:
                c_id = comp["id_comprobante"]
                alumno_nom = comp.get("alumno_nombre", "Alumno")
                monto_txt = f"$ {comp.get('total', 0):,.2f}"

                async def ver_pdf_click(_, cid=c_id):
                    token = getattr(page, "auth_token", "") or ""
                    url_pdf = (
                        f"{api_client.base_url_navegador}"
                        f"/finanzas/comprobantes/{cid}/archivo?token={token}"
                    )
                    await page.launch_url(url_pdf, web_popup_window_name="_blank")

                def abrir_modal_aprobar(_, c=comp):
                    dialogo = ft.AlertDialog(
                        shape=ft.RoundedRectangleBorder(radius=CARD_RADIUS),
                        title=ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE, color=ONLINE_GREEN, size=24
                                ),
                                ft.Text(
                                    "Confirmar Aprobación de Pago",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                            ],
                        ),
                        content=ft.Column(
                            tight=True,
                            spacing=10,
                            controls=[
                                ft.Text(
                                    f"¿Deseás validar y aprobar el comprobante #{c['id_comprobante']}?",
                                    size=14,
                                    color=TEXT_COLOR,
                                ),
                                ft.Container(
                                    padding=12,
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=BORDER_RADIUS,
                                    content=ft.Column(
                                        spacing=4,
                                        controls=[
                                            ft.Text(
                                                f"• Alumno: {c.get('alumno_nombre')} (Legajo #{c.get('legajo_alumno')})",
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEAL_DARK,
                                            ),
                                            ft.Text(
                                                f"• Curso: {c.get('curso')}",
                                                size=12,
                                                color=TEXT_COLOR,
                                            ),
                                            ft.Text(
                                                f"• Período: {c.get('mes'):02d}/{c.get('anio')} · Total: $ {c.get('total', 0):,.2f}",
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                                color=ONLINE_GREEN,
                                            ),
                                            ft.Text(
                                                f"• Conceptos: {c.get('conceptos')}",
                                                size=11,
                                                color=MUTED,
                                            ),
                                        ],
                                    ),
                                ),
                                ft.Text(
                                    "⚠️ Al aprobar, la factura asociada quedará registrada automáticamente como PAGADA.",
                                    size=12,
                                    color=MUTED,
                                ),
                            ],
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda _, d=None: None),
                            ft.Button(
                                "Aprobar y Saldar Factura",
                                bgcolor=ONLINE_GREEN,
                                color=BG_WHITE,
                                icon=ft.Icons.CHECK,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(
                                        radius=BORDER_RADIUS
                                    )
                                ),
                                on_click=lambda _,
                                cid=c["id_comprobante"]: page.run_task(
                                    ejecutar_aprobar, cid, dialogo
                                ),
                            ),
                        ],
                    )
                    dialogo.actions[0].on_click = lambda _: cerrar_dlg(dialogo)
                    page.overlay.append(dialogo)
                    dialogo.open = True
                    page.update()

                def abrir_modal_rechazar(_, c=comp):
                    dialogo = ft.AlertDialog(
                        shape=ft.RoundedRectangleBorder(radius=CARD_RADIUS),
                        title=ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(
                                    ft.Icons.CANCEL_OUTLINED,
                                    color=BADGE_RED_TXT,
                                    size=24,
                                ),
                                ft.Text(
                                    "Rechazar Comprobante",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=BADGE_RED_TXT,
                                ),
                            ],
                        ),
                        content=ft.Column(
                            tight=True,
                            spacing=10,
                            controls=[
                                ft.Text(
                                    f"¿Deseás rechazar el comprobante #{c['id_comprobante']}?",
                                    size=14,
                                    color=TEXT_COLOR,
                                ),
                                ft.Text(
                                    f"• Alumno: {c.get('alumno_nombre')}\n• Período: {c.get('mes'):02d}/{c.get('anio')} · Monto: $ {c.get('total', 0):,.2f}",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=TEXT_COLOR,
                                ),
                                ft.Text(
                                    "La cuota volverá a estado PENDIENTE para que la familia pueda informar nuevamente.",
                                    size=12,
                                    color=MUTED,
                                ),
                            ],
                        ),
                        actions=[
                            ft.TextButton("Cancelar", on_click=lambda _: None),
                            ft.Button(
                                "Rechazar Comprobante",
                                bgcolor=BADGE_RED_TXT,
                                color=BG_WHITE,
                                icon=ft.Icons.CLOSE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(
                                        radius=BORDER_RADIUS
                                    )
                                ),
                                on_click=lambda _,
                                cid=c["id_comprobante"]: page.run_task(
                                    ejecutar_rechazar, cid, dialogo
                                ),
                            ),
                        ],
                    )
                    dialogo.actions[0].on_click = lambda _: cerrar_dlg(dialogo)
                    page.overlay.append(dialogo)
                    dialogo.open = True
                    page.update()

                filas_tabla.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Text(
                                    comp.get("fecha_subida", "-"),
                                    size=12,
                                    color=TEXT_COLOR,
                                )
                            ),
                            ft.DataCell(
                                ft.Column(
                                    spacing=2,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            comp.get("alumno_nombre", "-"),
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT_COLOR,
                                        ),
                                        ft.Text(
                                            f"Legajo #{comp.get('legajo_alumno')} · {comp.get('curso')}",
                                            size=11,
                                            color=MUTED,
                                        ),
                                    ],
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    f"{comp.get('mes'):02d}/{comp.get('anio')}",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_COLOR,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    monto_txt,
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=ONLINE_GREEN,
                                )
                            ),
                            ft.DataCell(
                                ft.Button(
                                    content=ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.PICTURE_AS_PDF,
                                                size=14,
                                                color=TEAL_DARK,
                                            ),
                                            ft.Text(
                                                "Ver PDF",
                                                size=11,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEAL_DARK,
                                            ),
                                        ],
                                    ),
                                    tooltip=f"Comprobante / Constancia: {comp.get('archivo_url', '')}",
                                    bgcolor=TEAL_LIGHT,
                                    height=30,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(
                                            radius=BORDER_RADIUS
                                        ),
                                        padding=ft.Padding(10, 4, 10, 4),
                                    ),
                                    on_click=ver_pdf_click,
                                )
                            ),
                            ft.DataCell(
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Button(
                                            content=ft.Row(
                                                spacing=4,
                                                controls=[
                                                    ft.Icon(
                                                        ft.Icons.CHECK,
                                                        size=14,
                                                        color=BG_WHITE,
                                                    ),
                                                    ft.Text(
                                                        "Aprobar",
                                                        size=12,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=BG_WHITE,
                                                    ),
                                                ],
                                            ),
                                            bgcolor=ONLINE_GREEN,
                                            height=32,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BORDER_RADIUS
                                                ),
                                                padding=ft.Padding(10, 6, 10, 6),
                                            ),
                                            on_click=abrir_modal_aprobar,
                                        ),
                                        ft.Button(
                                            content=ft.Row(
                                                spacing=4,
                                                controls=[
                                                    ft.Icon(
                                                        ft.Icons.CLOSE,
                                                        size=14,
                                                        color=BG_WHITE,
                                                    ),
                                                    ft.Text(
                                                        "Rechazar",
                                                        size=12,
                                                        weight=ft.FontWeight.BOLD,
                                                        color=BG_WHITE,
                                                    ),
                                                ],
                                            ),
                                            bgcolor=BADGE_RED_TXT,
                                            height=32,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BORDER_RADIUS
                                                ),
                                                padding=ft.Padding(10, 6, 10, 6),
                                            ),
                                            on_click=abrir_modal_rechazar,
                                        ),
                                    ],
                                )
                            ),
                        ]
                    )
                )

            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(
                        ft.Text(
                            "Fecha",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                            color=TEXT_COLOR,
                        )
                    ),
                    ft.DataColumn(
                        ft.Text(
                            "Estudiante / Legajo",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                            color=TEXT_COLOR,
                        )
                    ),
                    ft.DataColumn(
                        ft.Text(
                            "Período",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                            color=TEXT_COLOR,
                        )
                    ),
                    ft.DataColumn(
                        ft.Text(
                            "Monto",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                            color=TEXT_COLOR,
                        )
                    ),
                    ft.DataColumn(
                        ft.Text(
                            "Comprobante",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                            color=TEXT_COLOR,
                        )
                    ),
                    ft.DataColumn(
                        ft.Text(
                            "Validación",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                            color=TEXT_COLOR,
                        )
                    ),
                ],
                rows=filas_tabla,
                heading_row_color=TEAL_LIGHT,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=BORDER_RADIUS,
                data_row_min_height=52,
            )

            lista_comprobantes_holder.controls = [
                ft.Container(
                    bgcolor=BG_WHITE,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=CARD_RADIUS,
                    padding=16,
                    content=ft.Column(scroll=ft.ScrollMode.ADAPTIVE, controls=[tabla]),
                )
            ]
            page.update()
        except Exception as ex:
            lista_comprobantes_holder.controls = [
                ft.Text(f"Error al cargar comprobantes: {ex}", color=BADGE_RED_TXT)
            ]
            page.update()

    card_comprobantes = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=36,
                                    height=36,
                                    bgcolor=TEAL_LIGHT,
                                    border_radius=BORDER_RADIUS,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(
                                        ft.Icons.FACT_CHECK_OUTLINED,
                                        color=TEAL_DARK,
                                        size=20,
                                    ),
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            "Comprobantes de Pago en Revisión",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEAL_DARK,
                                        ),
                                        ft.Text(
                                            "Auditá las transferencias informadas por los tutores para validar y cancelar sus facturas.",
                                            size=12,
                                            color=MUTED,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                badge_comprobantes,
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    tooltip="Actualizar lista",
                                    icon_color=TEAL_DARK,
                                    on_click=lambda _: page.run_task(
                                        cargar_comprobantes
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                lista_comprobantes_holder,
            ],
        ),
    )

    # Ejecutar al entrar a la pantalla
    page.run_task(cargar_datos)

    card_deportes = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    "Precios de Disciplinas Deportivas",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                lista_deportes,
            ],
        ),
    )

    btn_reportes = ft.Button(
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ANALYTICS_OUTLINED, color=TEAL_DARK, size=18),
                ft.Text(
                    "Ver Listados y Reportes Financieros",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
            ],
        ),
        bgcolor=TEAL_LIGHT,
        height=40,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
        on_click=lambda _: page.go("/admin/reportes-financieros"),
    )

    return admin_layout(
        page=page,
        titulo="Gestión de Precios y Finanzas",
        active_route="/admin/finanzas",
        content_controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[btn_reportes],
            ),
            aviso,
            card_comprobantes,
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(expand=True, spacing=24, controls=[card_fijos]),
                    ft.Column(expand=True, spacing=24, controls=[card_deportes]),
                ],
            ),
        ],
    )
