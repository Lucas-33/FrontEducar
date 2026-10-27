import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.portal_layout import portal_layout
from frontend.app.components.table_view import (
    create_pagination_bar,
    create_table_container,
    create_table_header,
)


def _plural(cantidad: int, singular: str, plural: str) -> str:
    """Devuelve 'N singular' o 'N plural' según corresponda."""
    return f"{cantidad} {singular if cantidad == 1 else plural}"


def _nombre_docente(perfil: dict | None, legajo: int | None) -> str:
    """Extrae el nombre legible del docente desde 'vinculacion' (ej: 'Docente: Gómez, Laura (#2001)')."""
    vinculo = (perfil or {}).get("vinculacion") or ""
    if ":" in vinculo:
        vinculo = vinculo.split(":", 1)[1]
    vinculo = vinculo.split("(#", 1)[0].strip()
    return vinculo or (f"Docente #{legajo}" if legajo else "Docente")


async def get_docente_materias_view(page: ft.Page) -> ft.Row:
    """Vista de materias y cursos asignados al docente, conectada a la API."""

    # ==================== 0. IDENTIDAD DEL DOCENTE ====================
    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    legajo_docente = (perfil or {}).get("legajo_profesor")

    def tarjeta_sin_identidad() -> ft.Container:
        return ft.Container(
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=48,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.PERSON_OFF_OUTLINED, size=44, color=MUTED),
                    ft.Text(
                        "No se pudo identificar al docente.",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                    ft.Text(
                        "Inicie sesión nuevamente para consultar sus materias asignadas.",
                        size=13,
                        color=MUTED,
                    ),
                ],
            ),
        )

    if not legajo_docente:
        return portal_layout(
            page=page,
            titulo="Mis Cursos y Materias Asignadas",
            active_route="/portal/docente/materias",
            rol="Docente",
            usuario_nombre="Docente",
            usuario_sub="Sesión no identificada",
            content_controls=[tarjeta_sin_identidad()],
        )

    # ==================== 1. CARGA DE DATOS REALES ====================
    estado: dict = {"asignaciones": [], "alumnos": [], "texto": "", "nivel": "Todos"}
    hubo_error = False

    try:
        asignaciones = await api_client.get_asignaciones()
    except Exception:
        asignaciones = []
        hubo_error = True
    estado["asignaciones"] = [
        a for a in asignaciones if a.get("legajo_profesor") == legajo_docente
    ]

    try:
        estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
    except Exception:
        estado["alumnos"] = []
        hubo_error = True

    niveles_disponibles = sorted(
        {a.get("nivel") for a in estado["asignaciones"] if a.get("nivel")}
    )

    def alumnos_de_curso(id_curso) -> list[dict]:
        return [a for a in estado["alumnos"] if a.get("id_curso") == id_curso]

    # ==================== 2. BARRA DE FILTROS ====================
    search_field = ft.TextField(
        hint_text="Buscar materia, curso o nivel...",
        hint_style=ft.TextStyle(size=14, color=MUTED),
        text_size=14,
        color=TEXT_COLOR,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(0, 0, 0, 10),
        expand=True,
    )
    search_input = ft.Container(
        width=300,
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

    filtro_nivel_container = ft.Container(
        width=200,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=ft.Dropdown(
            hint_text="Nivel: Todos",
            hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
            text_size=14,
            border=ft.InputBorder.NONE,
            content_padding=ft.Padding(12, 0, 8, 12),
            options=[ft.dropdown.Option("Todos")]
            + [ft.dropdown.Option(n) for n in niveles_disponibles],
        ),
    )
    filtro_nivel_dropdown: ft.Dropdown = filtro_nivel_container.content

    btn_actualizar = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SYNC, size=16, color=BG_WHITE),
                ft.Text(
                    "Actualizar", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
                ),
            ],
        ),
        bgcolor=TEAL,
        height=CONTROL_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            padding=ft.Padding(24, 12, 24, 12),
        ),
    )

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[search_input, filtro_nivel_container],
            ),
            btn_actualizar,
        ],
    )

    aviso_error = ft.Text(
        "⚠️ Algunas asignaciones no se pudieron cargar desde el backend."
        if hubo_error
        else "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        visible=hubo_error,
    )

    # ==================== 3. TABLA DE ASIGNACIONES ====================
    columnas = [
        ("ID", 90, False),
        ("Asignatura / Materia", 240, False),
        ("Curso Asignado", 180, False),
        ("Nivel Educativo", 170, False),
        ("Alumnos del Curso", 170, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def materia_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=90,
                        content=ft.Text(
                            f"#{item.get('id_materia', '-')}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=240,
                        content=ft.Text(
                            item.get("materia") or "-",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(item.get("curso") or "-", size=14, color=TEAL),
                    ),
                    ft.Container(
                        width=170,
                        content=ft.Text(item.get("nivel") or "-", size=13, color=MUTED),
                    ),
                    ft.Container(
                        width=170,
                        content=ft.Text(
                            _plural(
                                len(alumnos_de_curso(item.get("id_curso"))),
                                "alumno",
                                "alumnos",
                            ),
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Button(
                            "Ver Alumnos",
                            height=30,
                            bgcolor=TEAL_LIGHT,
                            color=TEAL_DARK,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=6),
                                padding=ft.Padding(10, 4, 10, 4),
                                text_style=ft.TextStyle(
                                    size=12, weight=ft.FontWeight.W_600
                                ),
                            ),
                            on_click=lambda _: page.go("/portal/docente/alumnos"),
                        ),
                    ),
                ],
            ),
        )

    def asignaciones_filtradas() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for a in estado["asignaciones"]:
            nivel = a.get("nivel") or ""
            if estado["nivel"] != "Todos" and nivel != estado["nivel"]:
                continue
            if (
                texto
                and texto
                not in f"{a.get('materia', '')} {a.get('curso', '')} {nivel}".lower()
            ):
                continue
            resultado.append(a)
        return resultado

    def render():
        visibles = asignaciones_filtradas()
        if estado["asignaciones"]:
            mensaje_vacio = "No hay materias que coincidan con los filtros."
        else:
            mensaje_vacio = "No tiene materias asignadas registradas en el sistema."
        table_holder.content = create_table_container(
            header=header_table,
            rows=[materia_row(a) for a in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(mensaje_vacio, size=13, color=MUTED),
                )
            ],
            min_width=1030,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['asignaciones'])} asignaciones",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar(e=None):
        try:
            asignaciones = await api_client.get_asignaciones()
            estado["asignaciones"] = [
                a for a in asignaciones if a.get("legajo_profesor") == legajo_docente
            ]
            estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
            niveles_actuales = sorted(
                {a.get("nivel") for a in estado["asignaciones"] if a.get("nivel")}
            )
            filtro_nivel_dropdown.options = [ft.dropdown.Option("Todos")] + [
                ft.dropdown.Option(n) for n in niveles_actuales
            ]
            aviso_error.visible = False
        except Exception as err:
            mostrar_error(f"No se pudieron refrescar las materias asignadas: {err}")
        actualizar_info()
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_nivel(e):
        estado["nivel"] = filtro_nivel_dropdown.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_nivel_dropdown.on_change = on_filtrar_nivel
    btn_actualizar.on_click = recargar

    # ==================== 4. TARJETA INFORMATIVA (RESUMEN REAL) ====================
    info_texto = ft.Text("", size=13, weight=ft.FontWeight.W_500, color=TEAL_DARK)

    def actualizar_info():
        ids_cursos_actuales = {
            a.get("id_curso")
            for a in estado["asignaciones"]
            if a.get("id_curso") is not None
        }
        ids_materias_actuales = {
            a.get("id_materia")
            for a in estado["asignaciones"]
            if a.get("id_materia") is not None
        }
        total_alumnos_actual = len(
            [a for a in estado["alumnos"] if a.get("id_curso") in ids_cursos_actuales]
        )
        info_texto.value = (
            f"Legajo #{legajo_docente}: "
            f"{_plural(len(ids_materias_actuales), 'materia', 'materias')} en "
            f"{_plural(len(ids_cursos_actuales), 'curso', 'cursos')} asignados · "
            f"{_plural(total_alumnos_actual, 'alumno', 'alumnos')} en sus divisiones."
        )

    info_card = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                info_texto,
            ],
        ),
    )

    actualizar_info()
    render()

    # ==================== 5. RETORNO CON PORTAL_LAYOUT ====================
    return portal_layout(
        page=page,
        titulo="Mis Cursos y Materias Asignadas",
        active_route="/portal/docente/materias",
        rol="Docente",
        usuario_nombre=_nombre_docente(perfil, legajo_docente),
        usuario_sub=f"Legajo #{legajo_docente}",
        content_controls=[
            info_card,
            filters_bar,
            aviso_error,
            table_holder,
            pagination_holder,
        ],
    )
