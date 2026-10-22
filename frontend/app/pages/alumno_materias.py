import flet as ft

from frontend.app.api_client import api_client
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
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


def _estado_vacio(titulo: str, mensaje: str) -> ft.Container:
    """Tarjeta de estado vacío para cuando el alumno no puede identificarse."""
    return ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=40,
        content=ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=56,
                    height=56,
                    bgcolor=TEAL_LIGHT,
                    border_radius=28,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.PERSON_OFF_OUTLINED, size=26, color=TEAL_DARK
                    ),
                ),
                ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text(mensaje, size=14, color=MUTED, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )


async def get_alumno_materias_view(page: ft.Page) -> ft.Row:
    """Retorna las materias y docentes asignados al curso real del alumno."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    legajo = (perfil or {}).get("legajo_alumno")

    def construir_layout(
        usuario_nombre: str, usuario_sub: str, controles: list[ft.Control]
    ) -> ft.Row:
        return portal_layout(
            page=page,
            titulo="Mis Materias y Profesores",
            active_route="/portal/alumno/materias",
            rol="Alumno",
            usuario_nombre=usuario_nombre,
            usuario_sub=usuario_sub,
            content_controls=controles,
        )

    if perfil is None or legajo is None:
        return construir_layout(
            "Estudiante",
            "Sesión no identificada",
            [
                _estado_vacio(
                    "Alumno no identificado",
                    "No se pudo identificar al alumno. Inicie sesión nuevamente.",
                )
            ],
        )

    # ==================== 1. DATOS REALES DEL ALUMNO Y SU CURSO ====================
    estado: dict = {"alumno": None, "curso": None, "nivel": None, "asignaciones": []}
    errores: list[str] = []

    try:
        alumnos = await api_client.get_alumnos(solo_activos=False)
        estado["alumno"] = next((a for a in alumnos if a.get("legajo") == legajo), None)
    except Exception:
        errores.append("datos del alumno")

    try:
        cursos = await api_client.get_cursos()
    except Exception:
        cursos = []
        errores.append("cursos")

    try:
        niveles = await api_client.get_niveles()
    except Exception:
        niveles = []

    try:
        asignaciones = await api_client.get_asignaciones()
    except Exception:
        asignaciones = []
        errores.append("asignaciones de materias")

    alumno = estado["alumno"]
    if alumno is None:
        return construir_layout(
            "Estudiante",
            f"Legajo #{legajo}",
            [
                _estado_vacio(
                    "Registro de alumno no encontrado",
                    f"No se encontró el legajo #{legajo} en el padrón de alumnos. "
                    "Verifique su matrícula con la Secretaría del colegio.",
                )
            ],
        )

    estado["curso"] = next(
        (c for c in cursos if c.get("id_curso") == alumno.get("id_curso")), None
    )
    estado["nivel"] = next(
        (
            n
            for n in niveles
            if estado["curso"] and n.get("id_nivel") == estado["curso"].get("id_nivel")
        ),
        None,
    )
    estado["asignaciones"] = [
        a
        for a in asignaciones
        if estado["curso"] and a.get("id_curso") == estado["curso"].get("id_curso")
    ]

    curso = estado["curso"]
    nombre_curso = curso.get("nombre") if curso else "Curso sin asignar"
    nombre_nivel = estado["nivel"].get("nombre") if estado["nivel"] else "Sin nivel"
    nombre_completo = (
        f"{alumno.get('nombre', '')} {alumno.get('apellido', '')}".strip() or "Alumno"
    )

    # ==================== 2. AVISO DE ERROR DE CARGA ====================
    aviso_error = ft.Text(
        f"⚠️ No se pudieron cargar: {', '.join(errores)}." if errores else "",
        size=13,
        weight=ft.FontWeight.W_600,
        color=BADGE_RED_TXT,
        visible=bool(errores),
    )

    # ==================== 3. TABLA DE MATERIAS DEL CURSO ====================
    columnas = [
        ("Materia", 240, False),
        ("Docente a Cargo", 260, False),
        ("Curso / División", 200, False),
        ("Nivel Educativo", 180, False),
        ("Legajo Docente", 140, True),
    ]

    header_table = create_table_header(columnas)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

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
                        width=240,
                        content=ft.Text(
                            item.get("materia", "-"),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=260,
                        content=ft.Text(
                            item.get("profesor", "-"), size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            item.get("curso", nombre_curso), size=13, color=TEXT_COLOR
                        ),
                    ),
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            item.get("nivel", nombre_nivel), size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=140,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Text(
                            f"#{item.get('legajo_profesor', '-')}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                ],
            ),
        )

    def render():
        visibles = estado["asignaciones"]
        table_holder.content = create_table_container(
            header=header_table,
            rows=[materia_row(m) for m in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        f"No hay materias asignadas al curso {nombre_curso} todavía.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
            min_width=1060,
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['asignaciones'])} asignaciones registradas",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    # ==================== 4. AVISO INFORMATIVO REAL ====================
    if estado["asignaciones"]:
        texto_info = (
            f"{nombre_curso} ({nombre_nivel}): {len(estado['asignaciones'])} asignaciones docentes registradas. "
            "Si una materia aparece más de una vez, se dicta con más de un docente."
        )
    else:
        texto_info = (
            f"No hay materias asignadas al curso {nombre_curso} ({nombre_nivel})."
        )

    info_card = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=16,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                ft.Text(texto_info, size=13, color=TEAL_DARK),
            ],
        ),
    )

    render()

    # ==================== 5. RETORNO CON PORTAL_LAYOUT ====================
    return construir_layout(
        nombre_completo,
        f"Legajo #{alumno.get('legajo')} · {nombre_curso}",
        [aviso_error, info_card, table_holder, pagination_holder],
    )
