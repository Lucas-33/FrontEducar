import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
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
from frontend.app.components.portal_layout import portal_layout


async def get_padre_facturas_view(page: ft.Page) -> ft.Container:
    """Vista móvil y responsiva para la gestión de facturas, desglose de deuda y pagos de los tutores."""

    # Estado reactivo local
    todas_las_facturas: list[dict] = []
    filtro_alumno_actual: str = "TODOS"
    filtro_estado_actual: str = "PENDIENTES"  # "PENDIENTES", "PAGADAS", "TODAS"
    factura_seleccionada: dict | None = None

    # Contenedores dinámicos
    lista_facturas_container = ft.Column(spacing=14)
    resumen_deuda_txt = ft.Text(
        "Calculando...", size=26, weight=ft.FontWeight.BOLD, color=TEAL_DARK
    )
    subtitulo_deuda_txt = ft.Text("Cargando estado de cuenta...", size=12, color=MUTED)
    selector_hijos_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
    tabs_estado_row = ft.Row(spacing=8, alignment=ft.MainAxisAlignment.START)

    # ==================== MODAL DE PAGO / TRANSFERENCIA ====================
    modal_titulo_alumno = ft.Text(
        "", size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK
    )
    modal_monto_txt = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color=TEAL_DARK)
    input_comprobante = ft.TextField(
        label="Nombre del archivo o N° de transferencia",
        hint_text="Ej: comprobante_banco_nacion_12345.pdf",
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
        height=42,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
    )

    def cerrar_dialogo_pago(_=None):
        dialogo_pago.open = False
        page.update()

    async def enviar_comprobante_click(_):
        nonlocal factura_seleccionada
        if not factura_seleccionada:
            return

        nombre_archivo = (input_comprobante.value or "").strip()
        if not nombre_archivo:
            snack_error = ft.SnackBar(
                ft.Text(
                    "Debe indicar el nombre o número del comprobante.", color=BG_WHITE
                ),
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

            await api_client.post_comprobante(
                id_factura=factura_seleccionada["id"],
                archivo_url=nombre_archivo,
            )

            cerrar_dialogo_pago()

            snack_exito = ft.SnackBar(
                ft.Text(
                    "¡Comprobante enviado con éxito! En revisión por Administración.",
                    color=BG_WHITE,
                ),
                bgcolor=ONLINE_GREEN,
            )
            page.overlay.append(snack_exito)
            snack_exito.open = True

            # Recargar facturas para reflejar el comprobante en tiempo real
            await cargar_facturas()

        except Exception as ex:
            snack_err = ft.SnackBar(
                ft.Text(f"Error al enviar comprobante: {ex}", color=BG_WHITE),
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
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.PAYMENTS_OUTLINED, color=TEAL, size=24),
                ft.Text(
                    "Informar Transferencia Bancaria",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
            ],
        ),
        content=ft.Container(
            width=420,
            content=ft.Column(
                tight=True,
                spacing=14,
                controls=[
                    modal_titulo_alumno,
                    ft.Container(
                        bgcolor=TEAL_LIGHT,
                        padding=12,
                        border_radius=BORDER_RADIUS,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    "Total a Abonar:",
                                    size=13,
                                    color=MUTED,
                                    weight=ft.FontWeight.W_600,
                                ),
                                modal_monto_txt,
                            ],
                        ),
                    ),
                    ft.Container(
                        bgcolor=BG_PAGE,
                        padding=12,
                        border_radius=BORDER_RADIUS,
                        border=ft.Border.all(1, BORDER_COLOR),
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(
                                    "Datos de la cuenta institucional:",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(
                                    "Banco: Banco de la Nación Argentina",
                                    size=11,
                                    color=TEXT_COLOR,
                                ),
                                ft.Text(
                                    "Titular: Educar para Transformar SRL",
                                    size=11,
                                    color=TEXT_COLOR,
                                ),
                                ft.Text(
                                    "CBU: 0110599520000012345678",
                                    size=11,
                                    color=TEXT_COLOR,
                                    selectable=True,
                                ),
                                ft.Text(
                                    "Alias: EDUCAR.COLEGIO.TRANS",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL,
                                    selectable=True,
                                ),
                            ],
                        ),
                    ),
                    ft.Text(
                        "Adjuntá el comprobante emitido por tu banco para que la administración valide el pago:",
                        size=12,
                        color=MUTED,
                    ),
                    input_comprobante,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo_pago),
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

    # ==================== RENDERIZADO DE CADA FACTURA (MOBILE CARD) ====================
    def crear_tarjeta_factura(factura: dict) -> ft.Container:
        estado = factura.get("estado", "PENDIENTE").upper()
        es_pagada = estado == "PAGADA"
        items = factura.get("items", [])
        comprobantes = factura.get("comprobantes", [])

        # Detección de comprobantes pendientes de revisión
        tiene_comprobante_pendiente = any(
            c.get("estado") == "PENDIENTE" for c in comprobantes
        )

        if es_pagada:
            color_badge_bg = BADGE_GREEN_BG
            color_badge_txt = BADGE_GREEN_TXT
            texto_estado = "PAGADA"
            icono_estado = ft.Icons.CHECK_CIRCLE
            color_icono = ONLINE_GREEN
        elif tiene_comprobante_pendiente:
            color_badge_bg = BADGE_YELLOW_BG
            color_badge_txt = BADGE_YELLOW_TXT
            texto_estado = "EN REVISIÓN"
            icono_estado = ft.Icons.HOURGLASS_TOP
            color_icono = AMBER_STATE
        else:
            color_badge_bg = BADGE_RED_BG
            color_badge_txt = BADGE_RED_TXT
            texto_estado = "PENDIENTE"
            icono_estado = ft.Icons.ERROR_OUTLINE
            color_icono = BADGE_RED_TXT

        # Encabezado principal de la tarjeta
        header_tarjeta = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=36,
                            height=36,
                            border_radius=18,
                            bgcolor=color_badge_bg,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(icono_estado, color=color_icono, size=20),
                        ),
                        ft.Column(
                            spacing=1,
                            controls=[
                                ft.Text(
                                    f"Período {factura.get('mes'):02d}/{factura.get('anio')}",
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_COLOR,
                                ),
                                ft.Text(
                                    factura.get("alumno_nombre", "Estudiante"),
                                    size=12,
                                    color=MUTED,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    bgcolor=color_badge_bg,
                    padding=ft.Padding(10, 4, 10, 4),
                    border_radius=12,
                    content=ft.Text(
                        texto_estado,
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=color_badge_txt,
                    ),
                ),
            ],
        )

        # Fila de Fechas y Total
        fila_montos = ft.Container(
            padding=ft.Padding.symmetric(vertical=8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=1,
                        controls=[
                            ft.Text("Vencimiento:", size=11, color=MUTED),
                            ft.Text(
                                str(factura.get("fecha_vencimiento", "-")),
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=TEXT_COLOR if es_pagada else BADGE_RED_TXT,
                            ),
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=1,
                        controls=[
                            ft.Text("Monto Total:", size=11, color=MUTED),
                            ft.Text(
                                f"$ {factura.get('total', 0):,.2f}",
                                size=17,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                        ],
                    ),
                ],
            ),
        )

        # ==================== DESGLOSE DE ÍTEMS (ACORDEÓN MÓVIL) ====================
        items_controls = []
        if items:
            for it in items:
                items_controls.append(
                    ft.Container(
                        padding=ft.Padding.symmetric(vertical=4),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(ft.Icons.CHECK, size=14, color=TEAL),
                                        ft.Text(
                                            it.get("concepto", "Concepto"),
                                            size=12,
                                            color=TEXT_COLOR,
                                        ),
                                    ],
                                ),
                                ft.Text(
                                    f"$ {it.get('monto', 0):,.2f}",
                                    size=12,
                                    weight=ft.FontWeight.W_600,
                                    color=TEXT_COLOR,
                                ),
                            ],
                        ),
                    )
                )
        else:
            items_controls.append(
                ft.Text(
                    "Cuota base institucional consolidada",
                    size=12,
                    color=MUTED,
                    italic=True,
                )
            )

        desglose_container = ft.Container(
            visible=False,
            bgcolor=BG_PAGE,
            padding=12,
            border_radius=BORDER_RADIUS,
            margin=ft.Margin.symmetric(vertical=6),
            content=ft.Column(spacing=2, controls=items_controls),
        )

        icono_flecha = ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=18, color=TEAL)
        texto_toggle = ft.Text(
            f"Ver desglose ({len(items)} conceptos)",
            size=12,
            weight=ft.FontWeight.W_600,
            color=TEAL,
        )

        def toggle_desglose(_):
            desglose_container.visible = not desglose_container.visible
            if desglose_container.visible:
                icono_flecha.name = ft.Icons.KEYBOARD_ARROW_UP
                texto_toggle.text = "Ocultar desglose de conceptos"
            else:
                icono_flecha.name = ft.Icons.KEYBOARD_ARROW_DOWN
                texto_toggle.text = f"Ver desglose ({len(items)} conceptos)"
            page.update()

        boton_toggle_desglose = ft.Container(
            on_click=toggle_desglose,
            padding=ft.Padding.symmetric(vertical=4),
            content=ft.Row(
                spacing=4,
                controls=[icono_flecha, texto_toggle],
            ),
        )

        # ==================== LISTA DE COMPROBANTES ASOCIADOS ====================
        comprobantes_seccion = []
        if comprobantes:
            comp_filas = []
            for c in comprobantes:
                c_estado = c.get("estado", "PENDIENTE").upper()
                c_color = (
                    ONLINE_GREEN
                    if c_estado == "APROBADO"
                    else (BADGE_RED_TXT if c_estado == "RECHAZADO" else AMBER_STATE)
                )
                comp_filas.append(
                    ft.Container(
                        padding=ft.Padding(8, 6, 8, 6),
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=6,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.ATTACH_FILE, size=15, color=MUTED
                                        ),
                                        ft.Text(
                                            str(
                                                c.get("archivo_url", "comprobante.pdf")
                                            ),
                                            size=11,
                                            color=TEXT_COLOR,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                    ],
                                ),
                                ft.Text(
                                    c_estado,
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color=c_color,
                                ),
                            ],
                        ),
                    )
                )
            comprobantes_seccion.append(
                ft.Container(
                    margin=ft.Margin(top=6, bottom=4, left=0, right=0),
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(
                                "Comprobantes informados:",
                                size=11,
                                color=MUTED,
                                weight=ft.FontWeight.W_600,
                            ),
                            *comp_filas,
                        ],
                    ),
                )
            )

        # ==================== BOTÓN DE ACCIÓN ====================
        acciones_tarjeta = []
        if not es_pagada:
            btn_accion = ft.Container(
                margin=ft.Margin(top=10, right=0, bottom=0, left=0),
                content=ft.Button(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.UPLOAD_FILE_OUTLINED, size=18, color=BG_WHITE
                            ),
                            ft.Text(
                                "Informar Transferencia",
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=BG_WHITE,
                            ),
                        ],
                    ),
                    bgcolor=TEAL,
                    height=40,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                    ),
                    on_click=lambda _, f=factura: abrir_modal_pago(f),
                ),
            )
            acciones_tarjeta.append(btn_accion)

        return ft.Container(
            bgcolor=BG_WHITE,
            padding=16,
            border_radius=CARD_RADIUS,
            border=ft.Border.all(1, BORDER_COLOR),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.04, "#000000"),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=4,
                controls=[
                    header_tarjeta,
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    fila_montos,
                    boton_toggle_desglose,
                    desglose_container,
                    *comprobantes_seccion,
                    *acciones_tarjeta,
                ],
            ),
        )

    # ==================== FILTRADO Y ACTUALIZACIÓN VISUAL ====================
    def refrescar_vista_filtrada():
        # 1. Filtro por alumno
        facturas_filtradas = todas_las_facturas
        if filtro_alumno_actual != "TODOS":
            facturas_filtradas = [
                f
                for f in facturas_filtradas
                if f.get("alumno_nombre") == filtro_alumno_actual
            ]

        # 2. Filtro por estado
        if filtro_estado_actual == "PENDIENTES":
            facturas_filtradas = [
                f
                for f in facturas_filtradas
                if f.get("estado", "PENDIENTE").upper() != "PAGADA"
            ]
        elif filtro_estado_actual == "PAGADAS":
            facturas_filtradas = [
                f
                for f in facturas_filtradas
                if f.get("estado", "PENDIENTE").upper() == "PAGADA"
            ]

        # 3. Renderizado de tarjetas
        if not facturas_filtradas:
            mensaje = (
                "¡Estás al día! No tenés cuotas pendientes de pago."
                if filtro_estado_actual == "PENDIENTES"
                else "No hay facturas registradas para el filtro seleccionado."
            )
            lista_facturas_container.controls = [
                ft.Container(
                    bgcolor=BG_WHITE,
                    padding=32,
                    border_radius=CARD_RADIUS,
                    border=ft.Border.all(1, BORDER_COLOR),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.VERIFIED_OUTLINED
                                if filtro_estado_actual == "PENDIENTES"
                                else ft.Icons.SEARCH_OFF,
                                size=40,
                                color=ONLINE_GREEN
                                if filtro_estado_actual == "PENDIENTES"
                                else MUTED,
                            ),
                            ft.Text(
                                mensaje,
                                size=13,
                                color=MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),
                )
            ]
        else:
            lista_facturas_container.controls = [
                crear_tarjeta_factura(f) for f in facturas_filtradas
            ]

        page.update()

    # ==================== CARGA DE DATOS DESDE LA API ====================
    async def cargar_facturas():
        nonlocal todas_las_facturas
        try:
            todas_las_facturas = await api_client.get_mis_facturas()

            # Cálculo de resumen
            pendientes = [
                f
                for f in todas_las_facturas
                if f.get("estado", "PENDIENTE").upper() != "PAGADA"
            ]
            pagadas = [
                f
                for f in todas_las_facturas
                if f.get("estado", "PENDIENTE").upper() == "PAGADA"
            ]
            total_deuda = sum(float(f.get("total", 0)) for f in pendientes)

            resumen_deuda_txt.value = f"$ {total_deuda:,.2f}"
            resumen_deuda_txt.color = BADGE_RED_TXT if total_deuda > 0 else ONLINE_GREEN

            if pendientes:
                subtitulo_deuda_txt.value = (
                    f"{len(pendientes)} cuota(s) pendiente(s) de pago"
                )
                subtitulo_deuda_txt.color = BADGE_RED_TXT
            else:
                subtitulo_deuda_txt.value = "Tu cuenta se encuentra al día"
                subtitulo_deuda_txt.color = ONLINE_GREEN

            # Poblar selector de hijos (Pills horizontales)
            nombres_hijos = sorted(
                {
                    f["alumno_nombre"]
                    for f in todas_las_facturas
                    if f.get("alumno_nombre")
                }
            )

            def cambiar_filtro_hijo(nombre: str):
                nonlocal filtro_alumno_actual
                filtro_alumno_actual = nombre
                actualizar_pills_hijos()
                refrescar_vista_filtrada()

            def actualizar_pills_hijos():
                pills = []
                opciones = ["TODOS", *nombres_hijos]
                for op in opciones:
                    es_activo = filtro_alumno_actual == op
                    etiqueta = "Todos mis hijos" if op == "TODOS" else op
                    pills.append(
                        ft.Container(
                            padding=ft.Padding(12, 6, 12, 6),
                            border_radius=16,
                            bgcolor=TEAL_DARK if es_activo else BG_WHITE,
                            border=ft.Border.all(
                                1, TEAL_DARK if es_activo else BORDER_COLOR
                            ),
                            on_click=lambda _, val=op: cambiar_filtro_hijo(val),
                            content=ft.Text(
                                etiqueta,
                                size=12,
                                weight=ft.FontWeight.BOLD
                                if es_activo
                                else ft.FontWeight.W_500,
                                color=BG_WHITE if es_activo else TEXT_COLOR,
                            ),
                        )
                    )
                selector_hijos_row.controls = pills

            actualizar_pills_hijos()

            # Poblar botones de estado (Pendientes / Pagadas / Todas)
            def cambiar_filtro_estado(nuevo_estado: str):
                nonlocal filtro_estado_actual
                filtro_estado_actual = nuevo_estado
                actualizar_tabs_estado()
                refrescar_vista_filtrada()

            def actualizar_tabs_estado():
                tabs = [
                    ("PENDIENTES", f"Pendientes ({len(pendientes)})"),
                    ("PAGADAS", f"Pagadas ({len(pagadas)})"),
                    ("TODAS", f"Todas ({len(todas_las_facturas)})"),
                ]
                botones_tab = []
                for clave, label in tabs:
                    es_sel = filtro_estado_actual == clave
                    botones_tab.append(
                        ft.Container(
                            padding=ft.Padding(12, 6, 12, 6),
                            border_radius=8,
                            bgcolor=TEAL_LIGHT if es_sel else "transparent",
                            on_click=lambda _, val=clave: cambiar_filtro_estado(val),
                            content=ft.Text(
                                label,
                                size=12,
                                weight=ft.FontWeight.BOLD
                                if es_sel
                                else ft.FontWeight.W_500,
                                color=TEAL_DARK if es_sel else MUTED,
                            ),
                        )
                    )
                tabs_estado_row.controls = botones_tab

            actualizar_tabs_estado()
            refrescar_vista_filtrada()

        except Exception as ex:
            resumen_deuda_txt.value = "Error"
            resumen_deuda_txt.color = BADGE_RED_TXT
            subtitulo_deuda_txt.value = f"No se pudo cargar la información: {ex}"
            lista_facturas_container.controls = [
                ft.Text(f"Error de conexión: {ex}", color=BADGE_RED_TXT)
            ]
            page.update()

    # Iniciar la carga asíncrona
    page.run_task(cargar_facturas)

    # ==================== LAYOUT DE PÁGINA (MOBILE-FIRST) ====================
    tarjeta_resumen_superior = ft.Container(
        bgcolor=BG_WHITE,
        padding=20,
        border_radius=CARD_RADIUS,
        border=ft.Border.all(1, BORDER_COLOR),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            "Saldo Total Pendiente",
                            size=12,
                            color=MUTED,
                            weight=ft.FontWeight.W_600,
                        ),
                        resumen_deuda_txt,
                        subtitulo_deuda_txt,
                    ],
                ),
                ft.Container(
                    width=46,
                    height=46,
                    bgcolor=TEAL_LIGHT,
                    border_radius=23,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.RECEIPT_LONG, color=TEAL_DARK, size=24),
                ),
            ],
        ),
    )

    seccion_filtros = ft.Column(
        spacing=8,
        controls=[
            ft.Text(
                "Filtrar por estudiante:",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=MUTED,
            ),
            selector_hijos_row,
            ft.Container(height=4),
            tabs_estado_row,
        ],
    )

    contenido = [
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Facturas y Pagos",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_color=TEAL,
                    tooltip="Actualizar facturas",
                    on_click=lambda _: page.run_task(cargar_facturas),
                ),
            ],
        ),
        tarjeta_resumen_superior,
        seccion_filtros,
        ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
        lista_facturas_container,
    ]

    return portal_layout(
        page=page,
        titulo="Mis Facturas",
        active_route="/portal/padre/facturas",
        rol="Padre",
        content_controls=contenido,
    )
