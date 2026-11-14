import flet as ft

from mobile.api_client import mobile_api
from mobile.components.constants import (
    AMBER_STATE,
    BADGE_GREEN_BG,
    BADGE_GREEN_TXT,
    BADGE_RED_BG,
    BADGE_RED_TXT,
    BADGE_YELLOW_BG,
    BADGE_YELLOW_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def get_facturas_page(page: ft.Page) -> list[ft.Control]:
    """Pantalla móvil de Facturas, Deuda y Carga de Comprobantes."""

    todas_las_facturas: list[dict] = []
    filtro_alumno_actual: str = "TODOS"
    filtro_estado_actual: str = "PENDIENTES"
    factura_seleccionada: dict | None = None

    lista_facturas_col = ft.Column(spacing=12)
    selector_hijos_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
    tabs_estado_row = ft.Row(spacing=8, alignment=ft.MainAxisAlignment.START)

    # ==================== MODAL DE PAGO / TRANSFERENCIA ====================
    modal_titulo_alumno = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=TEAL_DARK
    )
    modal_monto_txt = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK)
    input_comprobante = ft.TextField(
        label="Archivo / N° de transferencia",
        hint_text="Ej: transferencia_123456.pdf",
        value="comprobante_transferencia.pdf",
        text_size=13,
        border_radius=BORDER_RADIUS,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        expand=True,
    )

    btn_confirmar_pago = ft.Button(
        "Enviar Comprobante",
        icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
        bgcolor=TEAL,
        color=BG_WHITE,
        height=40,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
    )

    def cerrar_dialogo(_=None):
        dialogo_pago.open = False
        page.update()

    async def enviar_comprobante_click(_):
        nonlocal factura_seleccionada
        if not factura_seleccionada:
            return

        nombre_archivo = (input_comprobante.value or "").strip()
        if not nombre_archivo:
            snack_error = ft.SnackBar(
                ft.Text("Indique el nombre o número del comprobante.", color=BG_WHITE),
                bgcolor=BADGE_RED_TXT,
            )
            page.overlay.append(snack_error)
            snack_error.open = True
            page.update()
            return

        try:
            btn_confirmar_pago.disabled = True
            btn_confirmar_pago.text = "Enviando..."
            page.update()

            await mobile_api.post_comprobante(
                id_factura=factura_seleccionada["id"],
                archivo_url=nombre_archivo,
            )

            cerrar_dialogo()

            snack_exito = ft.SnackBar(
                ft.Text(
                    "¡Comprobante enviado! En revisión por administración.",
                    color=BG_WHITE,
                ),
                bgcolor=ONLINE_GREEN,
            )
            page.overlay.append(snack_exito)
            snack_exito.open = True

            await cargar_facturas()

        except Exception as ex:
            snack_err = ft.SnackBar(
                ft.Text(f"Error al enviar: {ex}", color=BG_WHITE),
                bgcolor=BADGE_RED_TXT,
            )
            page.overlay.append(snack_err)
            snack_err.open = True
        finally:
            btn_confirmar_pago.disabled = False
            btn_confirmar_pago.text = "Enviar Comprobante"
            page.update()

    btn_confirmar_pago.on_click = enviar_comprobante_click

    dialogo_pago = ft.AlertDialog(
        shape=ft.RoundedRectangleBorder(radius=CARD_RADIUS),
        title=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.PAYMENTS_OUTLINED, color=TEAL, size=22),
                ft.Text(
                    "Informar Transferencia",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
            ],
        ),
        content=ft.Container(
            width=360,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    modal_titulo_alumno,
                    ft.Container(
                        bgcolor=TEAL_LIGHT,
                        padding=10,
                        border_radius=BORDER_RADIUS,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    "Total a Abonar:",
                                    size=12,
                                    color=MUTED,
                                    weight=ft.FontWeight.W_600,
                                ),
                                modal_monto_txt,
                            ],
                        ),
                    ),
                    ft.Container(
                        bgcolor=BG_PAGE,
                        padding=10,
                        border_radius=BORDER_RADIUS,
                        border=ft.Border.all(1, BORDER_COLOR),
                        content=ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "Cuenta Escolar:",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(
                                    "Banco: Banco de la Nación Argentina",
                                    size=10,
                                    color=TEXT_COLOR,
                                ),
                                ft.Text(
                                    "CBU: 0110599520000012345678",
                                    size=10,
                                    color=TEXT_COLOR,
                                    selectable=True,
                                ),
                                ft.Text(
                                    "Alias: EDUCAR.COLEGIO.TRANS",
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL,
                                    selectable=True,
                                ),
                            ],
                        ),
                    ),
                    ft.Text(
                        "Adjuntá el ticket de pago emitido por tu banco:",
                        size=11,
                        color=MUTED,
                    ),
                    input_comprobante,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            btn_confirmar_pago,
        ],
    )

    def abrir_modal_pago(factura: dict):
        nonlocal factura_seleccionada
        factura_seleccionada = factura
        modal_titulo_alumno.value = f"Período {factura.get('mes')}/{factura.get('anio')} · {factura.get('alumno_nombre')}"
        modal_monto_txt.value = f"$ {factura.get('total', 0):,.2f}"
        input_comprobante.value = f"ticket_pago_fac_{factura.get('id')}.pdf"

        if dialogo_pago not in page.overlay:
            page.overlay.append(dialogo_pago)
        dialogo_pago.open = True
        page.update()

    # ==================== TARJETA DE CADA FACTURA ====================
    def crear_tarjeta_factura(factura: dict) -> ft.Container:
        estado = factura.get("estado", "PENDIENTE").upper()
        es_pagada = estado == "PAGADA"
        items = factura.get("items", [])
        comprobantes = factura.get("comprobantes", [])

        tiene_pendiente = any(c.get("estado") == "PENDIENTE" for c in comprobantes)

        if es_pagada:
            c_bg = BADGE_GREEN_BG
            c_txt = BADGE_GREEN_TXT
            txt_estado = "PAGADA"
            icono = ft.Icons.CHECK_CIRCLE
            c_icono = ONLINE_GREEN
        elif tiene_pendiente:
            c_bg = BADGE_YELLOW_BG
            c_txt = BADGE_YELLOW_TXT
            txt_estado = "EN REVISIÓN"
            icono = ft.Icons.HOURGLASS_TOP
            c_icono = AMBER_STATE
        else:
            c_bg = BADGE_RED_BG
            c_txt = BADGE_RED_TXT
            txt_estado = "PENDIENTE"
            icono = ft.Icons.ERROR_OUTLINE
            c_icono = BADGE_RED_TXT

        # Desglose de ítems
        filas_items = []
        if items:
            for it in items:
                filas_items.append(
                    ft.Container(
                        padding=ft.Padding.symmetric(vertical=3),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=5,
                                    controls=[
                                        ft.Icon(ft.Icons.CHECK, size=13, color=TEAL),
                                        ft.Text(
                                            it.get("concepto", "Concepto"),
                                            size=11,
                                            color=TEXT_COLOR,
                                        ),
                                    ],
                                ),
                                ft.Text(
                                    f"$ {it.get('monto', 0):,.2f}",
                                    size=11,
                                    weight=ft.FontWeight.W_600,
                                    color=TEXT_COLOR,
                                ),
                            ],
                        ),
                    )
                )
        else:
            filas_items.append(
                ft.Text("Cuota consolidada", size=11, color=MUTED, italic=True)
            )

        desglose_col = ft.Container(
            visible=False,
            bgcolor=BG_PAGE,
            padding=10,
            border_radius=BORDER_RADIUS,
            margin=ft.Margin.symmetric(vertical=4),
            content=ft.Column(spacing=2, controls=filas_items),
        )

        icono_arrow = ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=TEAL)
        txt_toggle = ft.Text(
            f"Ver detalle ({len(items)} conceptos)",
            size=11,
            weight=ft.FontWeight.W_600,
            color=TEAL,
        )

        def toggle_detalle(_):
            desglose_col.visible = not desglose_col.visible
            if desglose_col.visible:
                icono_arrow.name = ft.Icons.KEYBOARD_ARROW_UP
                txt_toggle.text = "Ocultar conceptos"
            else:
                icono_arrow.name = ft.Icons.KEYBOARD_ARROW_DOWN
                txt_toggle.text = f"Ver detalle ({len(items)} conceptos)"
            page.update()

        # Comprobantes informados
        comprobantes_ui = []
        if comprobantes:
            comp_filas = []
            for c in comprobantes:
                st = c.get("estado", "PENDIENTE").upper()
                col = (
                    ONLINE_GREEN
                    if st == "APROBADO"
                    else (BADGE_RED_TXT if st == "RECHAZADO" else AMBER_STATE)
                )
                comp_filas.append(
                    ft.Container(
                        padding=ft.Padding(6, 4, 6, 4),
                        bgcolor=BG_PAGE,
                        border_radius=6,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=4,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.ATTACH_FILE, size=13, color=MUTED
                                        ),
                                        ft.Text(
                                            str(
                                                c.get("archivo_url", "comprobante.pdf")
                                            ),
                                            size=10,
                                            color=TEXT_COLOR,
                                        ),
                                    ],
                                ),
                                ft.Text(
                                    st, size=9, weight=ft.FontWeight.BOLD, color=col
                                ),
                            ],
                        ),
                    )
                )
            comprobantes_ui.append(
                ft.Container(
                    margin=ft.Margin(top=4, bottom=4, left=0, right=0),
                    content=ft.Column(
                        spacing=3,
                        controls=[
                            ft.Text(
                                "Comprobantes informados:",
                                size=10,
                                color=MUTED,
                                weight=ft.FontWeight.W_600,
                            ),
                            *comp_filas,
                        ],
                    ),
                )
            )

        # Botón para pagar
        boton_pagar = []
        if not es_pagada:
            boton_pagar.append(
                ft.Container(
                    margin=ft.Margin(top=8, right=0, bottom=0, left=0),
                    content=ft.Button(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Icon(
                                    ft.Icons.UPLOAD_FILE_OUTLINED,
                                    size=16,
                                    color=BG_WHITE,
                                ),
                                ft.Text(
                                    "Informar Transferencia",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=BG_WHITE,
                                ),
                            ],
                        ),
                        bgcolor=TEAL,
                        height=36,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                        ),
                        on_click=lambda _, f=factura: abrir_modal_pago(f),
                    ),
                )
            )

        return ft.Container(
            bgcolor=BG_WHITE,
            padding=14,
            border_radius=CARD_RADIUS,
            border=ft.Border.all(1, BORDER_COLOR),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        width=32,
                                        height=32,
                                        border_radius=16,
                                        bgcolor=c_bg,
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Icon(icono, color=c_icono, size=18),
                                    ),
                                    ft.Column(
                                        spacing=0,
                                        controls=[
                                            ft.Text(
                                                f"Período {factura.get('mes'):02d}/{factura.get('anio')}",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEXT_COLOR,
                                            ),
                                            ft.Text(
                                                factura.get(
                                                    "alumno_nombre", "Estudiante"
                                                ),
                                                size=11,
                                                color=MUTED,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                bgcolor=c_bg,
                                padding=ft.Padding(8, 3, 8, 3),
                                border_radius=10,
                                content=ft.Text(
                                    txt_estado,
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=c_txt,
                                ),
                            ),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=1,
                                controls=[
                                    ft.Text("Vencimiento:", size=10, color=MUTED),
                                    ft.Text(
                                        str(factura.get("fecha_vencimiento", "-")),
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_COLOR
                                        if es_pagada
                                        else BADGE_RED_TXT,
                                    ),
                                ],
                            ),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=1,
                                controls=[
                                    ft.Text("Total:", size=10, color=MUTED),
                                    ft.Text(
                                        f"$ {factura.get('total', 0):,.2f}",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEAL_DARK,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(
                        on_click=toggle_detalle,
                        padding=ft.Padding.symmetric(vertical=4),
                        content=ft.Row(spacing=4, controls=[icono_arrow, txt_toggle]),
                    ),
                    desglose_col,
                    *comprobantes_ui,
                    *boton_pagar,
                ],
            ),
        )

    # ==================== FILTRADO REACTIVO ====================
    def refrescar_lista():
        filtradas = todas_las_facturas
        if filtro_alumno_actual != "TODOS":
            filtradas = [
                f for f in filtradas if f.get("alumno_nombre") == filtro_alumno_actual
            ]

        if filtro_estado_actual == "PENDIENTES":
            filtradas = [
                f for f in filtradas if f.get("estado", "PENDIENTE").upper() != "PAGADA"
            ]
        elif filtro_estado_actual == "PAGADAS":
            filtradas = [
                f for f in filtradas if f.get("estado", "PENDIENTE").upper() == "PAGADA"
            ]

        if not filtradas:
            lista_facturas_col.controls = [
                ft.Container(
                    bgcolor=BG_WHITE,
                    padding=24,
                    border_radius=CARD_RADIUS,
                    border=ft.Border.all(1, BORDER_COLOR),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Icon(
                                ft.Icons.VERIFIED_OUTLINED
                                if filtro_estado_actual == "PENDIENTES"
                                else ft.Icons.SEARCH_OFF,
                                size=32,
                                color=ONLINE_GREEN
                                if filtro_estado_actual == "PENDIENTES"
                                else MUTED,
                            ),
                            ft.Text(
                                "No hay facturas para mostrar con este filtro.",
                                size=12,
                                color=MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            ]
        else:
            lista_facturas_col.controls = [crear_tarjeta_factura(f) for f in filtradas]
        page.update()

    async def cargar_facturas():
        nonlocal todas_las_facturas
        try:
            todas_las_facturas = await mobile_api.get_mis_facturas()

            # Selector de hijos
            nombres_hijos = sorted(
                {
                    f["alumno_nombre"]
                    for f in todas_las_facturas
                    if f.get("alumno_nombre")
                }
            )

            def cambiar_hijo(val):
                nonlocal filtro_alumno_actual
                filtro_alumno_actual = val
                actualizar_pills()
                refrescar_lista()

            def actualizar_pills():
                pills = []
                for op in ["TODOS", *nombres_hijos]:
                    es_sel = filtro_alumno_actual == op
                    pills.append(
                        ft.Container(
                            padding=ft.Padding(10, 5, 10, 5),
                            border_radius=14,
                            bgcolor=TEAL_DARK if es_sel else BG_WHITE,
                            border=ft.Border.all(
                                1, TEAL_DARK if es_sel else BORDER_COLOR
                            ),
                            on_click=lambda _, v=op: cambiar_hijo(v),
                            content=ft.Text(
                                "Todos los hijos" if op == "TODOS" else op,
                                size=11,
                                color=BG_WHITE if es_sel else TEXT_COLOR,
                                weight=ft.FontWeight.BOLD
                                if es_sel
                                else ft.FontWeight.W_500,
                            ),
                        )
                    )
                selector_hijos_row.controls = pills

            actualizar_pills()

            # Tabs de estado
            pend = len(
                [
                    f
                    for f in todas_las_facturas
                    if f.get("estado", "PENDIENTE").upper() != "PAGADA"
                ]
            )
            pag = len(
                [
                    f
                    for f in todas_las_facturas
                    if f.get("estado", "PENDIENTE").upper() == "PAGADA"
                ]
            )

            def cambiar_estado(st):
                nonlocal filtro_estado_actual
                filtro_estado_actual = st
                actualizar_tabs()
                refrescar_lista()

            def actualizar_tabs():
                tabs_data = [
                    ("PENDIENTES", f"Pendientes ({pend})"),
                    ("PAGADAS", f"Pagadas ({pag})"),
                    ("TODAS", f"Todas ({len(todas_las_facturas)})"),
                ]
                botones = []
                for k, lab in tabs_data:
                    es_activo = filtro_estado_actual == k
                    botones.append(
                        ft.Container(
                            padding=ft.Padding(10, 5, 10, 5),
                            border_radius=8,
                            bgcolor=TEAL_LIGHT if es_activo else "transparent",
                            on_click=lambda _, val=k: cambiar_estado(val),
                            content=ft.Text(
                                lab,
                                size=11,
                                weight=ft.FontWeight.BOLD
                                if es_activo
                                else ft.FontWeight.W_500,
                                color=TEAL_DARK if es_activo else MUTED,
                            ),
                        )
                    )
                tabs_estado_row.controls = botones

            actualizar_tabs()
            refrescar_lista()

        except Exception as ex:
            lista_facturas_col.controls = [
                ft.Text(f"Error al cargar facturas: {ex}", size=12, color=BADGE_RED_TXT)
            ]
            page.update()

    page.run_task(cargar_facturas)

    return [
        ft.Text(
            "Mis Cuotas y Pagos", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK
        ),
        ft.Column(
            spacing=6,
            controls=[
                ft.Text(
                    "Filtrar por estudiante:",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=MUTED,
                ),
                selector_hijos_row,
                ft.Container(height=2),
                tabs_estado_row,
            ],
        ),
        ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
        lista_facturas_col,
    ]
