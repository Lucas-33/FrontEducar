import flet as ft

from app.api_client import api_client
from app.components.admin_layout import admin_layout
from app.components.constants import (
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
    CONTROL_HEIGHT,
    MUTED,
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)

MESES_NOMBRE = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


async def get_admin_reportes_financieros_view(page: ft.Page) -> ft.Row:
    """Pantalla de reportes y auditoría financiera avanzada para el Administrador."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    # Estado local de la vista
    tab_activa = 0  # 0: Ingresos, 1: Pagos Completos, 2: Pagos Incompletos, 3: Deportes, 4: Transporte
    anio_seleccionado = 2026
    mes_seleccionado = 0  # 0 = Todos
    filtro_texto = ""

    datos_ingresos: dict = {}
    datos_completos: dict = {}
    datos_incompletos: dict = {}
    datos_deportes: dict = {}
    datos_transporte: dict = {}

    # Contenedores dinámicos
    kpis_container = ft.ResponsiveRow(columns=12, spacing=16, run_spacing=16)
    contenido_tabla_container = ft.Column(spacing=12, expand=True)
    aviso_estado = ft.Text("", size=13, weight=ft.FontWeight.W_600, visible=False)

    def mostrar_aviso(mensaje: str, es_error: bool = False):
        aviso_estado.value = mensaje
        aviso_estado.color = BADGE_RED_TXT if es_error else ONLINE_GREEN
        aviso_estado.visible = True
        page.update()

    # ==================== CONTROLES DE FILTRO (TEXTO NEGRO) ====================
    dropdown_anio = ft.Dropdown(
        label="Año",
        value=str(anio_seleccionado),
        width=130,
        height=CONTROL_HEIGHT,
        color=ft.Colors.BLACK,
        text_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
        label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        border_radius=BORDER_RADIUS,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        options=[
            ft.dropdown.Option("2026", "2026"),
            ft.dropdown.Option("2025", "2025"),
            ft.dropdown.Option("2024", "2024"),
        ],
    )

    dropdown_mes = ft.Dropdown(
        label="Mes",
        value="0",
        width=180,
        height=CONTROL_HEIGHT,
        color=ft.Colors.BLACK,
        text_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_600),
        label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        border_radius=BORDER_RADIUS,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        options=[
            ft.dropdown.Option("0", "Todos los meses"),
            *[ft.dropdown.Option(str(num), nom) for num, nom in MESES_NOMBRE.items()],
        ],
    )

    input_buscar = ft.TextField(
        label="Buscar por alumno o legajo",
        prefix_icon=ft.Icons.SEARCH,
        hint_text="Ej: Martínez o 1002",
        width=280,
        height=CONTROL_HEIGHT,
        color=ft.Colors.BLACK,
        text_size=13,
        text_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.W_500),
        label_style=ft.TextStyle(color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        border_radius=BORDER_RADIUS,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
    )

    def badge_estado(estado: str) -> ft.Container:
        est = str(estado).upper()
        if est in ("PAGADA", "PAGADO", "ACTIVO", "APROBADO"):
            bg, txt = BADGE_GREEN_BG, BADGE_GREEN_TXT
            label = "PAGADO"
        elif est in ("PENDIENTE", "DEUDA", "INCOMPLETO"):
            bg, txt = BADGE_RED_BG, BADGE_RED_TXT
            label = "PENDIENTE"
        else:
            bg, txt = BADGE_YELLOW_BG, BADGE_YELLOW_TXT
            label = est
        return ft.Container(
            bgcolor=bg,
            border_radius=12,
            padding=ft.Padding(10, 4, 10, 4),
            content=ft.Text(label, size=11, weight=ft.FontWeight.BOLD, color=txt),
        )

    def kpi_card(
        titulo: str,
        valor: str,
        subtitulo: str,
        icono: ft.IconData,
        color_icono: str = TEAL_DARK,
    ) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 3},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=16,
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=44,
                        height=44,
                        bgcolor=TEAL_LIGHT,
                        border_radius=BORDER_RADIUS,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, size=22, color=color_icono),
                    ),
                    ft.Column(
                        spacing=2,
                        expand=True,
                        controls=[
                            ft.Text(
                                valor,
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                titulo,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLACK,
                            ),
                            ft.Text(
                                subtitulo,
                                size=11,
                                color=ft.Colors.BLACK87,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ],
            ),
        )

    # ==================== FUNCIONES DE CARGA DE DATOS ====================
    async def cargar_datos():
        nonlocal \
            datos_ingresos, \
            datos_completos, \
            datos_incompletos, \
            datos_deportes, \
            datos_transporte
        anio = int(dropdown_anio.value or 2026)
        mes_val = int(dropdown_mes.value or 0)
        mes_param = mes_val if mes_val > 0 else None

        params = {"anio": anio}
        if mes_param:
            params["mes"] = mes_param

        try:
            if tab_activa == 0:
                datos_ingresos = await api_client.get_reporte_ingresos(params)
            elif tab_activa == 1:
                datos_completos = await api_client.get_reporte_pagos_completos(params)
            elif tab_activa == 2:
                datos_incompletos = await api_client.get_reporte_pagos_incompletos(
                    params
                )
            elif tab_activa == 3:
                datos_deportes = await api_client.get_reporte_pagos_deportes(params)
            elif tab_activa == 4:
                datos_transporte = await api_client.get_reporte_pagos_transporte(params)
        except Exception as ex:
            mostrar_aviso(f"Error al obtener datos: {ex}", es_error=True)

        renderizar_tab_actual()
        page.update()

    # ==================== RENDERIZADORES DE TABLAS (TEXTOS EN NEGRO) ====================
    def render_ingresos():
        items = datos_ingresos.get("items", [])
        busq = input_buscar.value.strip().lower()
        if busq:
            items = [
                it
                for it in items
                if busq in it["alumno_nombre"].lower()
                or busq in str(it["legajo_alumno"])
                or busq in str(it.get("dni", "")).lower()
                or busq in it["curso"].lower()
            ]

        # KPIs
        total = datos_ingresos.get("total_ingresos", 0.0)
        cantidad = datos_ingresos.get("cantidad_cobros", 0)
        promedio = datos_ingresos.get("promedio_cobro", 0.0)

        kpis_container.controls = [
            kpi_card(
                "Total Recaudado",
                f"$ {total:,.0f}",
                "Ingresos cobrados en período",
                ft.Icons.ATTACH_MONEY,
            ),
            kpi_card(
                "Cantidad de Cobros",
                str(cantidad),
                "Facturas liquidadas",
                ft.Icons.RECEIPT_LONG,
            ),
            kpi_card(
                "Promedio por Factura",
                f"$ {promedio:,.0f}",
                "Valor medio cobrado",
                ft.Icons.ANALYTICS,
            ),
            kpi_card(
                "Alumnos con Cobro",
                str(len({it["legajo_alumno"] for it in items})),
                "Estudiantes registrados",
                ft.Icons.PEOPLE_OUTLINE,
            ),
        ]

        if not items:
            return ft.Container(
                bgcolor=BG_WHITE,
                padding=40,
                border_radius=CARD_RADIUS,
                border=ft.Border.all(1, BORDER_COLOR),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "No se registraron ingresos en el período seleccionado.",
                    size=14,
                    color=ft.Colors.BLACK,
                ),
            )

        filas = []
        for it in items:
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                f"#{it['id_factura']}",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                f"{it['mes']:02d}/{it['anio']}",
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(it["fecha_emision"], size=12, color=ft.Colors.BLACK)
                        ),
                        ft.DataCell(
                            ft.Text(
                                str(it.get("dni", "-")), size=12, color=ft.Colors.BLACK
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                f"#{it['legajo_alumno']}",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                it["alumno_nombre"],
                                weight=ft.FontWeight.BOLD,
                                size=13,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                f"{it['curso']} ({it['nivel']})",
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                ", ".join(
                                    f"{c['concepto']}" for c in it.get("items", [])
                                ),
                                size=11,
                                color=ft.Colors.BLACK,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                f"$ {it['total']:,.0f}",
                                weight=ft.FontWeight.BOLD,
                                size=13,
                                color=ONLINE_GREEN,
                            )
                        ),
                        ft.DataCell(badge_estado(it["estado"])),
                    ]
                )
            )

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text(
                        "ID", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.BLACK
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Período",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Fecha",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "DNI",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Legajo",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Alumno",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Curso y Nivel",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Conceptos",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Monto Cobrado",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Estado",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
            ],
            rows=filas,
            heading_row_color=TEAL_LIGHT,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            data_row_min_height=48,
        )

        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=16,
            content=ft.Column(scroll=ft.ScrollMode.ADAPTIVE, controls=[tabla]),
        )

    def render_pagos_completos():
        total = datos_completos.get("total_recaudado", 0.0)
        cantidad = datos_completos.get("cantidad_pagos", 0)
        grupos = datos_completos.get("grupos_anio", [])

        kpis_container.controls = [
            kpi_card(
                "Total Pagado",
                f"$ {total:,.0f}",
                "Pagos completos registrados",
                ft.Icons.CHECK_CIRCLE_OUTLINE,
            ),
            kpi_card(
                "Facturas Canceladas",
                str(cantidad),
                "Total de cuotas 100% saldadas",
                ft.Icons.RECEIPT,
            ),
            kpi_card(
                "Años Auditados",
                str(len(grupos)),
                "Ciclos lectivos con ingresos",
                ft.Icons.CALENDAR_TODAY,
            ),
            kpi_card(
                "Cumplimiento",
                "Al Día",
                "Familias sin deuda pendiente",
                ft.Icons.VERIFIED,
                ONLINE_GREEN,
            ),
        ]

        if not grupos:
            return ft.Container(
                bgcolor=BG_WHITE,
                padding=40,
                border_radius=CARD_RADIUS,
                border=ft.Border.all(1, BORDER_COLOR),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "No se registran pagos completos en el período consultado.",
                    size=14,
                    color=ft.Colors.BLACK,
                ),
            )

        busq = input_buscar.value.strip().lower()
        bloques_anios = []

        for g in grupos:
            filas_curso = []
            subtotal_anio = 0.0

            for cur in g.get("cursos", []):
                alumnos_filtrados = [
                    al
                    for al in cur.get("alumnos", [])
                    if not busq
                    or busq in al["alumno_nombre"].lower()
                    or busq in str(al["legajo_alumno"])
                ]
                if not alumnos_filtrados:
                    continue

                subtotal_curso = sum(al["monto_pagado"] for al in alumnos_filtrados)
                subtotal_anio += subtotal_curso

                rows_tabla = [
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Text(
                                    f"#{al['id_factura']}",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    f"{al['mes']:02d}/{al['anio']}",
                                    size=12,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    str(al["legajo_alumno"]),
                                    size=12,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    al["alumno_nombre"],
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(al["dni"], size=12, color=ft.Colors.BLACK)
                            ),
                            ft.DataCell(
                                ft.Text(
                                    al["conceptos"], size=11, color=ft.Colors.BLACK87
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    f"$ {al['monto_pagado']:,.0f}",
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                    color=ONLINE_GREEN,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    al["fecha_pago"], size=12, color=ft.Colors.BLACK
                                )
                            ),
                            ft.DataCell(badge_estado("PAGADA")),
                        ]
                    )
                    for al in alumnos_filtrados
                ]

                tabla_curso = ft.DataTable(
                    columns=[
                        ft.DataColumn(
                            ft.Text(
                                "Fac #",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Período",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Legajo",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Alumno",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "DNI",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Conceptos",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Total ($)",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Fecha Pago",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Estado",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                    ],
                    rows=rows_tabla,
                    heading_row_color=TEAL_LIGHT,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=BORDER_RADIUS,
                )

                filas_curso.append(
                    ft.Container(
                        bgcolor=BG_PAGE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=BORDER_RADIUS,
                        padding=12,
                        margin=ft.Margin(0, 4, 0, 8),
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.SCHOOL,
                                                    size=18,
                                                    color=TEAL_DARK,
                                                ),
                                                ft.Text(
                                                    f"Curso: {cur['curso']}",
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.BLACK,
                                                ),
                                                ft.Text(
                                                    f"({len(alumnos_filtrados)} pagos)",
                                                    size=12,
                                                    color=ft.Colors.BLACK87,
                                                ),
                                            ],
                                        ),
                                        ft.Text(
                                            f"Subtotal Curso: $ {subtotal_curso:,.0f}",
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=ONLINE_GREEN,
                                        ),
                                    ],
                                ),
                                ft.Column(
                                    scroll=ft.ScrollMode.ADAPTIVE,
                                    controls=[tabla_curso],
                                ),
                            ],
                        ),
                    )
                )

            if filas_curso:
                bloques_anios.append(
                    ft.Container(
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=CARD_RADIUS,
                        padding=18,
                        margin=ft.Margin(0, 0, 0, 16),
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.CALENDAR_MONTH,
                                                    color=TEAL,
                                                    size=22,
                                                ),
                                                ft.Text(
                                                    f"Ciclo Lectivo / Año {g['anio']}",
                                                    size=18,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.BLACK,
                                                ),
                                            ],
                                        ),
                                        ft.Container(
                                            bgcolor=TEAL_LIGHT,
                                            padding=ft.Padding(12, 6, 12, 6),
                                            border_radius=BORDER_RADIUS,
                                            content=ft.Text(
                                                f"Total Año: $ {subtotal_anio:,.0f}",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEAL_DARK,
                                            ),
                                        ),
                                    ],
                                ),
                                ft.Divider(color=BORDER_COLOR, height=1),
                                *filas_curso,
                            ],
                        ),
                    )
                )

        return (
            ft.Column(controls=bloques_anios)
            if bloques_anios
            else ft.Text("Sin resultados.", color=ft.Colors.BLACK)
        )

    def render_pagos_incompletos():
        total = datos_incompletos.get("total_deuda", 0.0)
        cantidad = datos_incompletos.get("cantidad_incompletos", 0)
        grupos = datos_incompletos.get("grupos_anio", [])

        kpis_container.controls = [
            kpi_card(
                "Total en Mora / Deuda",
                f"$ {total:,.0f}",
                "Saldos pendientes de cobro",
                ft.Icons.MONEY_OFF,
                BADGE_RED_TXT,
            ),
            kpi_card(
                "Facturas Impagas",
                str(cantidad),
                "Cuotas sin saldar",
                ft.Icons.ERROR_OUTLINE,
                BADGE_RED_TXT,
            ),
            kpi_card(
                "Años con Deuda",
                str(len(grupos)),
                "Ciclos con morosidad registrada",
                ft.Icons.WARNING_AMBER,
                BADGE_RED_TXT,
            ),
            kpi_card(
                "Estado",
                "En Seguimiento",
                "Avisos enviados el día 20",
                ft.Icons.NOTIFICATIONS_ACTIVE,
                TEAL,
            ),
        ]

        if not grupos:
            return ft.Container(
                bgcolor=BG_WHITE,
                padding=40,
                border_radius=CARD_RADIUS,
                border=ft.Border.all(1, BORDER_COLOR),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "¡Excelente! No hay pagos pendientes ni deudas en el período.",
                    size=14,
                    color=ONLINE_GREEN,
                ),
            )

        busq = input_buscar.value.strip().lower()
        bloques_anios = []

        for g in grupos:
            filas_curso = []
            subtotal_anio = 0.0

            for cur in g.get("cursos", []):
                alumnos_filtrados = [
                    al
                    for al in cur.get("alumnos", [])
                    if not busq
                    or busq in al["alumno_nombre"].lower()
                    or busq in str(al["legajo_alumno"])
                ]
                if not alumnos_filtrados:
                    continue

                subtotal_curso = sum(al["saldo_pendiente"] for al in alumnos_filtrados)
                subtotal_anio += subtotal_curso

                rows_tabla = [
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Text(
                                    f"#{al['id_factura']}",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    f"{al['mes']:02d}/{al['anio']}",
                                    size=12,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    str(al["legajo_alumno"]),
                                    size=12,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    al["alumno_nombre"],
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(al["dni"], size=12, color=ft.Colors.BLACK)
                            ),
                            ft.DataCell(
                                ft.Text(
                                    al["conceptos"], size=11, color=ft.Colors.BLACK87
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    f"$ {al['saldo_pendiente']:,.0f}",
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                    color=BADGE_RED_TXT,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    al["fecha_vencimiento"],
                                    size=12,
                                    color=ft.Colors.BLACK,
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    f"{al['dias_mora']} días"
                                    if al["dias_mora"] > 0
                                    else "Al día",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=BADGE_RED_TXT
                                    if al["dias_mora"] > 0
                                    else ONLINE_GREEN,
                                )
                            ),
                            ft.DataCell(badge_estado("PENDIENTE")),
                        ]
                    )
                    for al in alumnos_filtrados
                ]

                tabla_curso = ft.DataTable(
                    columns=[
                        ft.DataColumn(
                            ft.Text(
                                "Fac #",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Período",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Legajo",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Alumno",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "DNI",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Conceptos Impagos",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Saldo Deuda ($)",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Vencimiento",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Mora",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataColumn(
                            ft.Text(
                                "Estado",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                color=ft.Colors.BLACK,
                            )
                        ),
                    ],
                    rows=rows_tabla,
                    heading_row_color=ft.Colors.RED_50,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=BORDER_RADIUS,
                )

                filas_curso.append(
                    ft.Container(
                        bgcolor=BG_PAGE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=BORDER_RADIUS,
                        padding=12,
                        margin=ft.Margin(0, 4, 0, 8),
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.SCHOOL,
                                                    size=18,
                                                    color=TEAL_DARK,
                                                ),
                                                ft.Text(
                                                    f"Curso: {cur['curso']}",
                                                    size=14,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.BLACK,
                                                ),
                                                ft.Text(
                                                    f"({len(alumnos_filtrados)} con deuda)",
                                                    size=12,
                                                    color=BADGE_RED_TXT,
                                                ),
                                            ],
                                        ),
                                        ft.Text(
                                            f"Deuda Curso: $ {subtotal_curso:,.0f}",
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=BADGE_RED_TXT,
                                        ),
                                    ],
                                ),
                                ft.Column(
                                    scroll=ft.ScrollMode.ADAPTIVE,
                                    controls=[tabla_curso],
                                ),
                            ],
                        ),
                    )
                )

            if filas_curso:
                bloques_anios.append(
                    ft.Container(
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=CARD_RADIUS,
                        padding=18,
                        margin=ft.Margin(0, 0, 0, 16),
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.CALENDAR_MONTH,
                                                    color=BADGE_RED_TXT,
                                                    size=22,
                                                ),
                                                ft.Text(
                                                    f"Deuda Año / Ciclo {g['anio']}",
                                                    size=18,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.BLACK,
                                                ),
                                            ],
                                        ),
                                        ft.Container(
                                            bgcolor=ft.Colors.RED_50,
                                            padding=ft.Padding(12, 6, 12, 6),
                                            border_radius=BORDER_RADIUS,
                                            content=ft.Text(
                                                f"Deuda Total Año: $ {subtotal_anio:,.0f}",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=BADGE_RED_TXT,
                                            ),
                                        ),
                                    ],
                                ),
                                ft.Divider(color=BORDER_COLOR, height=1),
                                *filas_curso,
                            ],
                        ),
                    )
                )

        return (
            ft.Column(controls=bloques_anios)
            if bloques_anios
            else ft.Text(
                "Sin morosos para el filtro seleccionado.", color=ft.Colors.BLACK
            )
        )

    def render_pagos_deportes():
        items = datos_deportes.get("items", [])
        busq = input_buscar.value.strip().lower()
        if busq:
            items = [
                it
                for it in items
                if busq in it["alumno_nombre"].lower()
                or busq in it["deporte"].lower()
                or busq in it["profesor"].lower()
                or busq in str(it["legajo_alumno"])
            ]

        total_rec = datos_deportes.get("total_recaudado", 0.0)
        inscriptos = datos_deportes.get("total_inscriptos", 0)
        al_dia = datos_deportes.get("al_dia", 0)
        morosos = datos_deportes.get("morosos", 0)

        kpis_container.controls = [
            kpi_card(
                "Recaudación Deportes",
                f"$ {total_rec:,.0f}",
                "Cuotas deportivas pagas",
                ft.Icons.SPORTS_SOCCER,
                TEAL,
            ),
            kpi_card(
                "Alumnos Inscriptos",
                str(inscriptos),
                "Total en disciplinas",
                ft.Icons.PEOPLE_OUTLINE,
            ),
            kpi_card(
                "Alumnos al Día",
                str(al_dia),
                "Con deporte cancelado",
                ft.Icons.CHECK_CIRCLE,
                ONLINE_GREEN,
            ),
            kpi_card(
                "Alumnos Morosos",
                str(morosos),
                "Cuota deporte pendiente",
                ft.Icons.WARNING,
                BADGE_RED_TXT,
            ),
        ]

        if not items:
            return ft.Container(
                bgcolor=BG_WHITE,
                padding=40,
                border_radius=CARD_RADIUS,
                border=ft.Border.all(1, BORDER_COLOR),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "No hay registros de inscripciones deportivas en el período.",
                    size=14,
                    color=ft.Colors.BLACK,
                ),
            )

        filas = []
        for it in items:
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.FITNESS_CENTER, size=16, color=TEAL
                                    ),
                                    ft.Text(
                                        it["deporte"],
                                        weight=ft.FontWeight.BOLD,
                                        size=13,
                                        color=ft.Colors.BLACK,
                                    ),
                                ],
                            )
                        ),
                        ft.DataCell(
                            ft.Text(it["nivel"], size=12, color=ft.Colors.BLACK)
                        ),
                        ft.DataCell(
                            ft.Text(it["horario"], size=11, color=ft.Colors.BLACK)
                        ),
                        ft.DataCell(
                            ft.Text(
                                it["profesor"],
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataCell(
                            ft.Column(
                                tight=True,
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        it["alumno_nombre"],
                                        weight=ft.FontWeight.BOLD,
                                        size=13,
                                        color=ft.Colors.BLACK,
                                    ),
                                    ft.Text(
                                        f"Legajo #{it['legajo_alumno']} · {it['curso']}",
                                        size=11,
                                        color=ft.Colors.BLACK87,
                                    ),
                                ],
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                f"$ {it['precio_deporte']:,.0f}",
                                weight=ft.FontWeight.BOLD,
                                size=13,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataCell(badge_estado(it["estado_pago"])),
                        ft.DataCell(
                            ft.Text(
                                it["fecha_referencia"], size=12, color=ft.Colors.BLACK
                            )
                        ),
                    ]
                )
            )

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text(
                        "Deporte",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Nivel Educativo",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Horario",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Profesor a Cargo",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Alumno / Curso",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Tarifa ($)",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Estado Pago",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Fecha",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
            ],
            rows=filas,
            heading_row_color=TEAL_LIGHT,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            data_row_min_height=48,
        )

        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=16,
            content=ft.Column(scroll=ft.ScrollMode.ADAPTIVE, controls=[tabla]),
        )

    def render_pagos_transporte():
        items = datos_transporte.get("items", [])
        busq = input_buscar.value.strip().lower()
        if busq:
            items = [
                it
                for it in items
                if busq in it["alumno_nombre"].lower()
                or busq in it["recorrido"].lower()
                or busq in str(it["legajo_alumno"])
            ]

        total_rec = datos_transporte.get("total_recaudado", 0.0)
        pasajeros = datos_transporte.get("total_pasajeros", 0)
        al_dia = datos_transporte.get("al_dia", 0)
        morosos = datos_transporte.get("morosos", 0)

        kpis_container.controls = [
            kpi_card(
                "Recaudación Transporte",
                f"$ {total_rec:,.0f}",
                "Boletos mensuales cobrados",
                ft.Icons.DIRECTIONS_BUS,
                TEAL,
            ),
            kpi_card(
                "Pasajeros Activos",
                str(pasajeros),
                "Inscriptos al servicio",
                ft.Icons.PEOPLE_OUTLINE,
            ),
            kpi_card(
                "Pasajeros al Día",
                str(al_dia),
                "Sin deuda de transporte",
                ft.Icons.CHECK_CIRCLE,
                ONLINE_GREEN,
            ),
            kpi_card(
                "Pasajeros en Mora",
                str(morosos),
                "Cuota transporte adeudada",
                ft.Icons.WARNING,
                BADGE_RED_TXT,
            ),
        ]

        if not items:
            return ft.Container(
                bgcolor=BG_WHITE,
                padding=40,
                border_radius=CARD_RADIUS,
                border=ft.Border.all(1, BORDER_COLOR),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "No hay registros de transporte escolar en el período.",
                    size=14,
                    color=ft.Colors.BLACK,
                ),
            )

        filas = []
        for it in items:
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.DIRECTIONS_BUS_FILLED,
                                        size=16,
                                        color=TEAL,
                                    ),
                                    ft.Text(
                                        it["recorrido"],
                                        weight=ft.FontWeight.BOLD,
                                        size=13,
                                        color=ft.Colors.BLACK,
                                    ),
                                ],
                            )
                        ),
                        ft.DataCell(
                            ft.Column(
                                tight=True,
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        it["alumno_nombre"],
                                        weight=ft.FontWeight.BOLD,
                                        size=13,
                                        color=ft.Colors.BLACK,
                                    ),
                                    ft.Text(
                                        f"Legajo #{it['legajo_alumno']} · DNI {it['dni']}",
                                        size=11,
                                        color=ft.Colors.BLACK87,
                                    ),
                                ],
                            )
                        ),
                        ft.DataCell(
                            ft.Text(it["curso"], size=12, color=ft.Colors.BLACK)
                        ),
                        ft.DataCell(
                            ft.Text(
                                f"$ {it['precio_mensual']:,.0f}",
                                weight=ft.FontWeight.BOLD,
                                size=13,
                                color=ft.Colors.BLACK,
                            )
                        ),
                        ft.DataCell(badge_estado(it["estado_pago"])),
                        ft.DataCell(
                            ft.Text(
                                it["fecha_referencia"], size=12, color=ft.Colors.BLACK
                            )
                        ),
                    ]
                )
            )

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(
                    ft.Text(
                        "Recorrido",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Alumno / Pasajero",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Curso",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Tarifa Mensual ($)",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Estado Pago",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
                ft.DataColumn(
                    ft.Text(
                        "Fecha Referencia",
                        weight=ft.FontWeight.BOLD,
                        size=12,
                        color=ft.Colors.BLACK,
                    )
                ),
            ],
            rows=filas,
            heading_row_color=TEAL_LIGHT,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            data_row_min_height=48,
        )

        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=16,
            content=ft.Column(scroll=ft.ScrollMode.ADAPTIVE, controls=[tabla]),
        )

    def renderizar_tab_actual():
        contenido_tabla_container.controls.clear()
        if tab_activa == 0:
            contenido_tabla_container.controls.append(render_ingresos())
        elif tab_activa == 1:
            contenido_tabla_container.controls.append(render_pagos_completos())
        elif tab_activa == 2:
            contenido_tabla_container.controls.append(render_pagos_incompletos())
        elif tab_activa == 3:
            contenido_tabla_container.controls.append(render_pagos_deportes())
        elif tab_activa == 4:
            contenido_tabla_container.controls.append(render_pagos_transporte())

    # ==================== NAVEGACIÓN POR PESTAÑAS ====================
    tabs_titulos = [
        ("Ingresos por Período", ft.Icons.ATTACH_MONEY),
        ("Pagos Completos (por Año y Alumno)", ft.Icons.CHECK_CIRCLE_OUTLINE),
        ("Pagos Incompletos / Deuda", ft.Icons.MONEY_OFF),
        ("Pagos por Deportes", ft.Icons.SPORTS_SOCCER),
        ("Pagos por Transporte", ft.Icons.DIRECTIONS_BUS),
    ]

    tabs_row = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)

    def renderizar_botones_tabs():
        tabs_row.controls.clear()
        for idx, (titulo, icono) in enumerate(tabs_titulos):
            activo = idx == tab_activa
            tabs_row.controls.append(
                ft.Container(
                    bgcolor=TEAL if activo else BG_WHITE,
                    border=ft.Border.all(1, TEAL if activo else BORDER_COLOR),
                    border_radius=BORDER_RADIUS,
                    padding=ft.Padding(16, 10, 16, 10),
                    on_click=lambda _, i=idx: seleccionar_tab(i),
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                icono, size=18, color=BG_WHITE if activo else TEAL_DARK
                            ),
                            ft.Text(
                                titulo,
                                size=13,
                                weight=ft.FontWeight.BOLD
                                if activo
                                else ft.FontWeight.W_500,
                                color=BG_WHITE if activo else ft.Colors.BLACK,
                            ),
                        ],
                    ),
                )
            )
        page.update()

    def seleccionar_tab(idx: int):
        nonlocal tab_activa
        tab_activa = idx
        renderizar_botones_tabs()
        page.run_task(cargar_datos)

    # ==================== BOTÓN EXPORTAR EXCEL (ASYNC / AWAIT) ====================
    async def exportar_excel_click(_):
        anio = int(dropdown_anio.value or 2026)
        mes_val = int(dropdown_mes.value or 0)
        params = {"anio": anio}
        if mes_val > 0:
            params["mes"] = mes_val

        nombre_archivo = "ingresos"
        if tab_activa == 0:
            nombre_archivo = "ingresos"
        elif tab_activa == 1:
            nombre_archivo = "pagos-completos"
        elif tab_activa == 2:
            nombre_archivo = "pagos-incompletos"
        elif tab_activa == 3:
            nombre_archivo = "pagos-deportes"
        elif tab_activa == 4:
            nombre_archivo = "pagos-transporte"

        url_descarga = api_client.reporte_url(nombre_archivo, params=params)
        try:
            await page.launch_url(url_descarga, web_popup_window_name="_blank")
        except Exception as ex:
            mostrar_aviso(f"Error al descargar Excel: {ex}", es_error=True)

    btn_exportar = ft.Button(
        content=ft.Row(
            spacing=6,
            controls=[
                ft.Icon(ft.Icons.FILE_DOWNLOAD_OUTLINED, size=16, color=TEAL_DARK),
                ft.Text(
                    "Exportar a Excel",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                ),
            ],
        ),
        bgcolor=TEAL_LIGHT,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
        on_click=exportar_excel_click,
    )

    btn_filtrar = ft.Button(
        content=ft.Row(
            spacing=6,
            controls=[
                ft.Icon(ft.Icons.FILTER_ALT, size=16, color=BG_WHITE),
                ft.Text("Filtrar", size=13, weight=ft.FontWeight.BOLD, color=BG_WHITE),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
        on_click=lambda _: page.run_task(cargar_datos),
    )

    input_buscar.on_change = lambda _: (renderizar_tab_actual(), page.update())

    # ==================== ESTRUCTURA PRINCIPAL DE LA VISTA ====================
    renderizar_botones_tabs()
    await cargar_datos()

    header_view = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        width=36,
                        height=36,
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=18,
                        alignment=ft.Alignment(0, 0),
                        tooltip="Volver al Centro de Reportes",
                        on_click=lambda _: page.go("/admin/reportes"),
                        content=ft.Icon(
                            ft.Icons.ARROW_BACK, size=16, color=ft.Colors.BLACK
                        ),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "Reportes y Listados Financieros",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                "Auditoría de ingresos, cobros completos, deudas por año y servicios escolares",
                                size=13,
                                color=ft.Colors.BLACK87,
                            ),
                        ],
                    ),
                ],
            ),
            btn_exportar,
        ],
    )

    filtros_bar = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=16,
        content=ft.Row(
            wrap=True,
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                dropdown_anio,
                dropdown_mes,
                input_buscar,
                btn_filtrar,
            ],
        ),
    )

    cuerpo = ft.Column(
        spacing=16,
        expand=True,
        controls=[
            header_view,
            aviso_estado,
            tabs_row,
            filtros_bar,
            kpis_container,
            contenido_tabla_container,
        ],
    )

    return admin_layout(
        page=page,
        titulo="Reportes y Listados Financieros",
        active_route="/admin/reportes",
        content_controls=[cuerpo],
    )
