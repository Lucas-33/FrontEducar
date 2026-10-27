import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_BG,
    BADGE_RED_TXT,
    BG_PAGE,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    GREEN_LIGHT,
    MUTED,
    ONLINE_GREEN,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def formatear_fecha(valor) -> str:
    """Convierte una fecha ISO (YYYY-MM-DD) al formato local DD/MM/YYYY."""
    texto = str(valor or "").strip()
    if not texto:
        return "—"
    partes = texto.split("-")
    if len(partes) == 3 and all(partes):
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return texto


async def get_admin_reporte_transporte_pasajeros_view(page: ft.Page) -> ft.Row:
    """Reporte de pasajeros del transporte escolar agrupados por recorrido, con datos reales."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    estado: dict = {
        "recorridos": [],
        "inscripciones": [],
        "alumnos": [],
        "cursos": [],
        "niveles": [],
        "texto": "",
        "recorrido": "Todos",
        "nivel": "Todos",
        "pasajero": "Todos",
    }
    errores: list[str] = []

    async def consultar(etiqueta: str, metodo, *args, **kwargs) -> list:
        """Ejecuta una consulta a la API y acumula los fallos para avisar en pantalla."""
        try:
            return await metodo(*args, **kwargs)
        except httpx.HTTPStatusError as err:
            detalle = "error del servidor"
            try:
                detalle = err.response.json().get("detail", detalle)
            except Exception:
                pass
            errores.append(f"{etiqueta}: {detalle}")
            return []
        except httpx.RequestError:
            errores.append(f"{etiqueta}: sin conexión con el backend")
            return []
        except Exception:
            errores.append(f"{etiqueta}: error inesperado")
            return []

    estado["recorridos"] = await consultar("recorridos", api_client.get_recorridos)
    estado["inscripciones"] = await consultar(
        "inscripciones de transporte", api_client.get_inscripciones_transporte
    )
    estado["alumnos"] = await consultar(
        "alumnos", api_client.get_alumnos, solo_activos=False
    )
    estado["cursos"] = await consultar("cursos", api_client.get_cursos)
    estado["niveles"] = await consultar("niveles", api_client.get_niveles)

    alumno_por_legajo = {a["legajo"]: a for a in estado["alumnos"]}
    curso_por_id = {c["id_curso"]: c for c in estado["cursos"]}
    nivel_por_id = {n["id_nivel"]: n["nombre"] for n in estado["niveles"]}

    def curso_del_pasajero(legajo) -> str:
        alumno = alumno_por_legajo.get(legajo)
        curso = curso_por_id.get(alumno.get("id_curso")) if alumno else None
        return curso["nombre"] if curso else "Sin curso asignado"

    def nivel_del_pasajero(legajo) -> str:
        alumno = alumno_por_legajo.get(legajo)
        curso = curso_por_id.get(alumno.get("id_curso")) if alumno else None
        if not curso:
            return "Sin nivel"
        return nivel_por_id.get(curso.get("id_nivel"), f"Nivel {curso.get('id_nivel')}")

    pasajeros_activos = len(
        [
            i
            for i in estado["inscripciones"]
            if str(i.get("estado", "")).upper() == "ACTIVO"
        ]
    )
    pasajeros_inactivos = len(estado["inscripciones"]) - pasajeros_activos

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )
    if errores:
        aviso_error.value = "⚠️ No se pudieron cargar algunos datos: " + " · ".join(
            errores
        )
        aviso_error.visible = True

    # ==================== 1. ENCABEZADO Y ACCIONES ====================
    header_actions = ft.Row(
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
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=18,
                        alignment=ft.Alignment(0, 0),
                        tooltip="Volver al Centro de Reportes",
                        on_click=lambda _: page.go("/admin/reportes"),
                        content=ft.Icon(ft.Icons.ARROW_BACK, size=16, color=TEXT_COLOR),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                "Hoja de Ruta: Pasajeros por Recorrido de Transporte",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                "Planilla operativa con estado de alta y datos de contacto de cada pasajero",
                                size=12,
                                color=MUTED,
                            ),
                        ],
                    ),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.Button(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(
                                    ft.Icons.FILE_DOWNLOAD_OUTLINED,
                                    size=15,
                                    color=TEAL_DARK,
                                ),
                                ft.Text(
                                    "Exportar Excel",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=TEAL_DARK,
                                ),
                            ],
                        ),
                        bgcolor=TEAL_LIGHT,
                        height=36,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                        ),
                        on_click=lambda _: page.launch_url(
                            api_client.reporte_url("transporte")
                        ),
                    ),
                    ft.Button(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(
                                    ft.Icons.PRINT_OUTLINED, size=15, color=BG_WHITE
                                ),
                                ft.Text(
                                    "Imprimir PDF",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=BG_WHITE,
                                ),
                            ],
                        ),
                        bgcolor=ORANGE,
                        height=36,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)
                        ),
                        on_click=lambda _: None,
                    ),
                ],
            ),
        ],
    )

    # ==================== 2. INDICADORES REALES ====================
    def kpi_card(
        titulo: str,
        valor: int,
        subtitulo: str,
        icono: ft.IconData,
        icono_color: str = TEAL_DARK,
        icono_bg: str = TEAL_LIGHT,
    ) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 3},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=12,
            padding=18,
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=40,
                        height=40,
                        bgcolor=icono_bg,
                        border_radius=BORDER_RADIUS,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, size=20, color=icono_color),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                str(valor),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                titulo,
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=TEXT_COLOR,
                            ),
                            ft.Text(
                                subtitulo,
                                size=11,
                                color=MUTED,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ],
            ),
        )

    kpis = ft.ResponsiveRow(
        columns=12,
        spacing=16,
        run_spacing=16,
        controls=[
            kpi_card(
                "Recorridos habilitados",
                len(estado["recorridos"]),
                "Rutas del servicio de transporte",
                ft.Icons.DIRECTIONS_BUS_OUTLINED,
            ),
            kpi_card(
                "Pasajeros registrados",
                len(estado["inscripciones"]),
                "Alumnos anotados en el servicio",
                ft.Icons.PEOPLE_OUTLINE,
            ),
            kpi_card(
                "Pasajeros activos",
                pasajeros_activos,
                "Altas vigentes en el servicio",
                ft.Icons.CHECK_CIRCLE_OUTLINE,
                ONLINE_GREEN,
                GREEN_LIGHT,
            ),
            kpi_card(
                "Pasajeros inactivos",
                pasajeros_inactivos,
                "Altas dadas de baja",
                ft.Icons.REMOVE_CIRCLE_OUTLINE,
                BADGE_RED_TXT,
                BADGE_RED_BG,
            ),
        ],
    )

    # ==================== 3. RESUMEN POR RECORRIDO ====================
    def recorrido_card(recorrido: dict) -> ft.Container:
        pasajeros = [
            i
            for i in estado["inscripciones"]
            if i.get("id_recorrido") == recorrido["id_recorrido"]
        ]
        total = len(pasajeros)
        activos = len(
            [p for p in pasajeros if str(p.get("estado", "")).upper() == "ACTIVO"]
        )
        ancho = int(220 * activos / total) if total else 0
        return ft.Container(
            col={"sm": 12, "md": 6},
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=18,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=32,
                                height=32,
                                bgcolor=TEAL_LIGHT,
                                border_radius=BORDER_RADIUS,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(
                                    ft.Icons.DIRECTIONS_BUS_OUTLINED,
                                    size=16,
                                    color=TEAL_DARK,
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    recorrido.get("descripcion")
                                    or f"Recorrido {recorrido.get('id_recorrido')}",
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEAL_DARK,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ),
                        ],
                    ),
                    ft.Text(
                        f"{total} pasajeros registrados · {activos} activos",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=TEAL,
                    ),
                    ft.Container(
                        width=220,
                        height=10,
                        bgcolor=BG_PAGE,
                        border_radius=5,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Row(
                            spacing=0,
                            controls=[
                                ft.Container(
                                    width=max(ancho, 4) if activos else 0,
                                    height=10,
                                    bgcolor=ONLINE_GREEN,
                                    border_radius=5,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    seccion_resumen = ft.Column(
        spacing=16,
        controls=[
            ft.Text(
                "Resumen de Pasajeros por Recorrido",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            ft.ResponsiveRow(
                columns=12,
                spacing=16,
                run_spacing=16,
                controls=[recorrido_card(r) for r in estado["recorridos"]]
                or [
                    ft.Container(
                        col={"sm": 12},
                        padding=20,
                        bgcolor=BG_WHITE,
                        border=ft.Border.all(1, BORDER_COLOR),
                        border_radius=CARD_RADIUS,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "No hay recorridos de transporte registrados en el sistema.",
                            size=13,
                            color=MUTED,
                        ),
                    )
                ],
            ),
        ],
    )

    # ==================== 4. FILTROS ====================
    search_field = ft.TextField(
        hint_text="Buscar alumno o legajo...",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(0, 0, 0, 10),
        expand=True,
    )
    search_input = ft.Container(
        width=280,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        padding=ft.Padding(12, 0, 12, 0),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SEARCH, size=16, color=MUTED),
                search_field,
            ],
        ),
    )

    def filtro_dropdown(hint: str, width: int, opciones: list[str]) -> ft.Container:
        return ft.Container(
            width=width,
            height=CONTROL_HEIGHT,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=BORDER_RADIUS,
            content=ft.Dropdown(
                hint_text=hint,
                hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
                text_size=14,
                border=ft.InputBorder.NONE,
                content_padding=ft.Padding(12, 0, 8, 12),
                options=[ft.dropdown.Option(opc) for opc in opciones],
            ),
        )

    filtro_recorrido_container = filtro_dropdown(
        "Recorrido: Todos",
        230,
        ["Todos"]
        + [
            r.get("descripcion") or f"Recorrido {r.get('id_recorrido')}"
            for r in estado["recorridos"]
        ],
    )
    filtro_recorrido: ft.Dropdown = filtro_recorrido_container.content
    filtro_nivel_container = filtro_dropdown(
        "Nivel: Todos", 150, ["Todos"] + [n["nombre"] for n in estado["niveles"]]
    )
    filtro_nivel: ft.Dropdown = filtro_nivel_container.content
    filtro_pasajero_container = filtro_dropdown(
        "Estado: Todos", 145, ["Todos", "Activo", "Inactivo"]
    )
    filtro_pasajero: ft.Dropdown = filtro_pasajero_container.content

    filters_bar = ft.Row(
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            search_input,
            filtro_recorrido_container,
            filtro_nivel_container,
            filtro_pasajero_container,
        ],
    )

    # ==================== 5. TABLA DE PASAJEROS ====================
    columnas_transporte = [
        ("Recorrido Oficial", 160, False),
        ("Legajo", 90, False),
        ("Alumno Pasajero", 180, False),
        ("Curso", 120, False),
        ("Domicilio / Parada", 220, False),
        ("Teléfono Registrado", 140, False),
        ("Fecha de Alta", 120, False),
        ("Estado", 90, False),
    ]
    header_table = create_table_header(columnas_transporte)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def pasajero_row(inscripcion: dict) -> ft.Container:
        legajo = inscripcion.get("legajo_alumno")
        alumno = alumno_por_legajo.get(legajo) or {}
        return ft.Container(
            height=50,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=160,
                        content=ft.Text(
                            inscripcion.get("recorrido") or "—",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=90,
                        content=ft.Text(
                            f"#{legajo}", size=13, weight=ft.FontWeight.BOLD, color=TEAL
                        ),
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            str(inscripcion.get("alumno", "")).split(" (")[0],
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            curso_del_pasajero(legajo), size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=220,
                        content=ft.Text(
                            alumno.get("domicilio") or "Sin domicilio registrado",
                            size=13,
                            color=TEXT_COLOR,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                    ft.Container(
                        width=140,
                        content=ft.Text(
                            alumno.get("telefono") or "Sin teléfono",
                            size=13,
                            color=MUTED,
                        ),
                    ),
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            formatear_fecha(inscripcion.get("fecha_alta")),
                            size=12,
                            color=MUTED,
                        ),
                    ),
                    ft.Container(
                        width=90,
                        content=status_badge(inscripcion.get("estado") or "Sin estado"),
                    ),
                ],
            ),
        )

    def pasajeros_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for inscripcion in estado["inscripciones"]:
            if (
                estado["recorrido"] != "Todos"
                and (inscripcion.get("recorrido") or "") != estado["recorrido"]
            ):
                continue
            if (
                estado["nivel"] != "Todos"
                and nivel_del_pasajero(inscripcion.get("legajo_alumno"))
                != estado["nivel"]
            ):
                continue
            if (
                estado["pasajero"] != "Todos"
                and str(inscripcion.get("estado") or "").capitalize()
                != estado["pasajero"]
            ):
                continue
            if (
                texto
                and texto
                not in f"{inscripcion.get('alumno', '')} {inscripcion.get('legajo_alumno', '')} {inscripcion.get('recorrido', '')}".lower()
            ):
                continue
            resultado.append(inscripcion)
        return resultado

    def render():
        visibles = pasajeros_filtrados()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[pasajero_row(p) for p in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay pasajeros que coincidan con los filtros aplicados.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
            min_width=1152,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['inscripciones'])} pasajeros registrados en el transporte escolar",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_recorrido(e):
        estado["recorrido"] = filtro_recorrido.value or "Todos"
        render()

    def on_filtrar_nivel(e):
        estado["nivel"] = filtro_nivel.value or "Todos"
        render()

    def on_filtrar_pasajero(e):
        estado["pasajero"] = filtro_pasajero.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_recorrido.on_select = on_filtrar_recorrido
    filtro_nivel.on_select = on_filtrar_nivel
    filtro_pasajero.on_select = on_filtrar_pasajero

    render()

    # ==================== 6. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Reporte: Alumnos por Recorrido de Transporte",
        active_route="/admin/reportes",
        content_controls=[
            header_actions,
            aviso_error,
            kpis,
            seccion_resumen,
            filters_bar,
            table_holder,
            pagination_holder,
        ],
    )
