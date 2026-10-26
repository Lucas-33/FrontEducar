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
from frontend.app.components.form_controls import status_badge
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


async def get_docente_alumnos_view(page: ft.Page) -> ft.Row:
    """Nómina de estudiantes de los cursos del docente, conectada a la API."""

    # ==================== 0. IDENTIDAD DEL DOCENTE ====================
    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
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
                        "Inicie sesión nuevamente para consultar la nómina de sus alumnos.",
                        size=13,
                        color=MUTED,
                    ),
                ],
            ),
        )

    if not legajo_docente:
        return portal_layout(
            page=page,
            titulo="Nómina de Alumnos de Mis Cursos",
            active_route="/portal/docente/alumnos",
            rol="Docente",
            usuario_nombre="Docente",
            usuario_sub="Sesión no identificada",
            content_controls=[tarjeta_sin_identidad()],
        )

    # ==================== 1. CARGA DE DATOS REALES ====================
    estado: dict = {
        "alumnos": [],
        "cursos": [],
        "texto": "",
        "curso": "Todos",
        "estado": "Todos",
    }
    hubo_error = False

    try:
        asignaciones = await api_client.get_asignaciones()
    except Exception:
        asignaciones = []
        hubo_error = True
    ids_cursos = {
        a.get("id_curso")
        for a in asignaciones
        if a.get("legajo_profesor") == legajo_docente
    }

    try:
        alumnos = await api_client.get_alumnos(solo_activos=False)
    except Exception:
        alumnos = []
        hubo_error = True
    estado["alumnos"] = [a for a in alumnos if a.get("id_curso") in ids_cursos]

    try:
        cursos = await api_client.get_cursos()
    except Exception:
        cursos = []
        hubo_error = True
    estado["cursos"] = [c for c in cursos if c.get("id_curso") in ids_cursos]

    nombre_curso = {
        c.get("id_curso"): c.get("nombre") or f"Curso {c.get('id_curso')}"
        for c in estado["cursos"]
    }
    for id_curso in ids_cursos:
        nombre_curso.setdefault(id_curso, f"Curso {id_curso}")

    def estado_legible(alumno: dict) -> str:
        return (alumno.get("estado_alumno") or "Sin estado").strip().capitalize()

    # ==================== 2. BARRA DE FILTROS ====================
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

    opciones_cursos = ["Todos"] + sorted(nombre_curso.values())
    filtro_curso_container = filtro_dropdown("Curso: Todos", 200, opciones_cursos)
    filtro_estado_container = filtro_dropdown(
        "Estado: Todos", 160, ["Todos", "Activo", "Inactivo"]
    )
    filtro_curso_dropdown: ft.Dropdown = filtro_curso_container.content
    filtro_estado_dropdown: ft.Dropdown = filtro_estado_container.content

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
                controls=[
                    search_input,
                    filtro_curso_container,
                    filtro_estado_container,
                ],
            ),
            btn_actualizar,
        ],
    )

    aviso_error = ft.Text(
        "⚠️ Algunos datos de la nómina no se pudieron cargar desde el backend."
        if hubo_error
        else "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        visible=hubo_error,
    )

    # ==================== 3. TABLA DE ALUMNOS ====================
    columnas_alumnos = [
        ("Legajo", 110, False),
        ("Apellido", 190, False),
        ("Nombre", 190, False),
        ("Curso", 180, False),
        ("Estado", 130, False),
    ]

    header_table = create_table_header(columnas_alumnos)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def alumno_row(item: dict) -> ft.Container:
        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            f"#{item.get('legajo', '-')}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=190,
                        content=ft.Text(
                            item.get("apellido") or "-",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=190,
                        content=ft.Text(
                            item.get("nombre") or "-", size=14, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            nombre_curso.get(
                                item.get("id_curso"),
                                f"Curso {item.get('id_curso', '-')}",
                            ),
                            size=13,
                            color=MUTED,
                        ),
                    ),
                    ft.Container(width=130, content=status_badge(estado_legible(item))),
                ],
            ),
        )

    def alumnos_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for a in estado["alumnos"]:
            if estado["curso"] != "Todos":
                if nombre_curso.get(a.get("id_curso")) != estado["curso"]:
                    continue
            if estado["estado"] != "Todos" and estado_legible(a) != estado["estado"]:
                continue
            if texto and texto not in (
                f"{a.get('apellido', '')} {a.get('nombre', '')} {a.get('legajo', '')}".lower()
            ):
                continue
            resultado.append(a)
        return resultado

    def render():
        visibles = alumnos_filtrados()
        if estado["alumnos"]:
            mensaje_vacio = "No hay alumnos que coincidan con los filtros."
        else:
            mensaje_vacio = (
                "No hay alumnos registrados en los cursos asignados a su legajo."
            )
        table_holder.content = create_table_container(
            header=header_table,
            rows=[alumno_row(a) for a in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(mensaje_vacio, size=13, color=MUTED),
                )
            ],
            min_width=860,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['alumnos'])} alumnos en sus cursos",
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
            ids_cursos_actuales = {
                a.get("id_curso")
                for a in asignaciones
                if a.get("legajo_profesor") == legajo_docente
            }
            alumnos = await api_client.get_alumnos(solo_activos=False)
            estado["alumnos"] = [
                a for a in alumnos if a.get("id_curso") in ids_cursos_actuales
            ]
            cursos = await api_client.get_cursos()
            estado["cursos"] = [
                c for c in cursos if c.get("id_curso") in ids_cursos_actuales
            ]
            nombre_curso.clear()
            nombre_curso.update(
                {
                    c.get("id_curso"): c.get("nombre") or f"Curso {c.get('id_curso')}"
                    for c in estado["cursos"]
                }
            )
            for id_curso in ids_cursos_actuales:
                nombre_curso.setdefault(id_curso, f"Curso {id_curso}")
            filtro_curso_dropdown.options = [ft.dropdown.Option("Todos")] + [
                ft.dropdown.Option(opc) for opc in sorted(nombre_curso.values())
            ]
            aviso_error.visible = False
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la nómina de alumnos: {err}")
        actualizar_info()
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_curso(e):
        estado["curso"] = filtro_curso_dropdown.value or "Todos"
        render()

    def on_filtrar_estado(e):
        estado["estado"] = filtro_estado_dropdown.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_curso_dropdown.on_change = on_filtrar_curso
    filtro_estado_dropdown.on_change = on_filtrar_estado
    btn_actualizar.on_click = recargar

    # ==================== 4. TARJETA INFORMATIVA (RESUMEN REAL) ====================
    info_texto = ft.Text("", size=13, weight=ft.FontWeight.W_500, color=TEAL_DARK)

    def actualizar_info():
        activos_actuales = len(
            [a for a in estado["alumnos"] if estado_legible(a) == "Activo"]
        )
        info_texto.value = (
            f"Legajo #{legajo_docente}: {_plural(len(estado['alumnos']), 'alumno', 'alumnos')} en "
            f"{_plural(len(estado['cursos']), 'curso', 'cursos')} asignados · "
            f"{_plural(activos_actuales, 'activo', 'activos')} en la nómina."
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
        titulo="Nómina de Alumnos de Mis Cursos",
        active_route="/portal/docente/alumnos",
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
