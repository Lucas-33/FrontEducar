import flet as ft
from frontend.app.api_client import api_client
from frontend.app.components.constants import (
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
    BADGE_RED_TXT,
)
from frontend.app.components.portal_layout import portal_layout
from frontend.app.components.table_view import (
    create_table_container,
    create_table_header,
)


def _nombre_completo(persona: dict) -> str:
    nombre = (persona.get("nombre") or "").strip()
    apellido = (persona.get("apellido") or "").strip()
    return f"{nombre} {apellido}".strip() or "Alumno sin nombre"


def _texto_seguro(valor) -> str:
    if valor is None:
        return "-"
    texto = str(valor).strip()
    return texto or "-"


def _estado_vacio(mensaje: str, icono: ft.IconData = ft.Icons.INFO_OUTLINE) -> ft.Container:
    """Tarjeta de estado vacío o error, manteniendo el layout y sin datos ficticios."""
    return ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=40,
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icono, size=36, color=MUTED),
                ft.Text(mensaje, size=14, color=MUTED, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )


async def get_padre_docentes_view(page: ft.Page) -> ft.Row:
    """Nómina real de docentes por materia para los cursos de los hijos del tutor."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    try:
        perfil = await api_client.get_mi_perfil()
    except Exception:
        perfil = None

    nombre_tutor = perfil.get("username", "Tutor") if perfil else "Tutor"

    def layout(controles: list[ft.Control]) -> ft.Row:
        return portal_layout(
            page=page,
            titulo="Cuerpo Docente por Materia",
            active_route="/portal/padre/docentes",
            rol="Padre",
            usuario_nombre=nombre_tutor,
            usuario_sub="Tutor responsable",
            content_controls=controles,
        )

    id_padre = (perfil or {}).get("id_padre")
    if not perfil or not id_padre:
        return layout(
            [
                _estado_vacio(
                    "No se pudo identificar al tutor. Inicie sesión nuevamente.",
                    ft.Icons.PERSON_OFF_OUTLINED,
                )
            ]
        )

    estado: dict = {
        "hijos": [],
        "cursos": [],
        "niveles": [],
        "asignaciones": [],
        "profesores": [],
        "texto": "",
        "legajo": None,
    }

    try:
        estado["hijos"] = await api_client.get_hijos(id_padre)
    except Exception:
        estado["hijos"] = []

    if not estado["hijos"]:
        return layout([_estado_vacio("No hay alumnos vinculados a esta cuenta.", ft.Icons.FAMILY_RESTROOM_OUTLINED)])

    estado["legajo"] = estado["hijos"][0].get("legajo")

    cargadores = (
        ("cursos", api_client.get_cursos),
        ("niveles", api_client.get_niveles),
        ("asignaciones", api_client.get_asignaciones),
        ("profesores", lambda: api_client.get_profesores(solo_activos=False)),
    )
    for clave, cargador in cargadores:
        try:
            estado[clave] = await cargador()
        except Exception:
            estado[clave] = []

    cursos_por_id = {c.get("id_curso"): c for c in estado["cursos"]}
    niveles_por_id = {n.get("id_nivel"): n for n in estado["niveles"]}
    profesores_por_legajo = {p.get("legajo"): p for p in estado["profesores"]}

    def hijo_seleccionado() -> dict | None:
        for h in estado["hijos"]:
            if h.get("legajo") == estado["legajo"]:
                return h
        return None

    def curso_de(hijo: dict) -> dict | None:
        return cursos_por_id.get(hijo.get("id_curso"))

    def nivel_de(hijo: dict) -> dict | None:
        curso = curso_de(hijo)
        return niveles_por_id.get(curso.get("id_nivel")) if curso else None

    def etiqueta_hijo(hijo: dict) -> str:
        curso = curso_de(hijo)
        curso_nombre = curso.get("nombre") if curso else "Sin curso"
        return f"{_nombre_completo(hijo)} — {curso_nombre}"

    def docentes_del_hijo(hijo: dict | None) -> list[dict]:
        if not hijo:
            return []
        id_curso = hijo.get("id_curso")
        vistos: set = set()
        resultado: list[dict] = []
        for asignacion in estado["asignaciones"]:
            if asignacion.get("id_curso") != id_curso:
                continue
            clave = (asignacion.get("id_materia"), asignacion.get("legajo_profesor"))
            if clave in vistos:
                continue
            vistos.add(clave)
            resultado.append(asignacion)
        return resultado

    # ==================== 1. FILTROS ====================
    search_field = ft.TextField(
        hint_text="Buscar materia o docente...",
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

    alumno_dropdown = ft.Dropdown(
        hint_text="Alumno",
        hint_style=ft.TextStyle(size=14, color=TEXT_COLOR),
        text_size=14,
        border=ft.InputBorder.NONE,
        content_padding=ft.Padding(12, 0, 8, 12),
        options=[
            ft.dropdown.Option(key=str(h.get("legajo")), text=etiqueta_hijo(h)) for h in estado["hijos"]
        ],
        value=str(estado["legajo"]),
    )
    alumno_selector = ft.Container(
        width=340,
        height=CONTROL_HEIGHT,
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=BORDER_RADIUS,
        content=alumno_dropdown,
    )

    btn_refrescar = ft.IconButton(
        icon=ft.Icons.REFRESH,
        icon_size=18,
        icon_color=TEAL,
        tooltip="Actualizar nómina docente",
    )

    filters_bar = ft.Row(
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        controls=[
            ft.Text("Filtrar por alumno:", size=14, weight=ft.FontWeight.W_600, color=TEAL_DARK),
            alumno_selector,
            search_input,
            btn_refrescar,
        ],
    )

    aviso_error = ft.Text("", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False)

    # ==================== 2. TABLA DE DOCENTES ====================
    columnas = [
        ("Asignatura / Materia", 220, False),
        ("Profesor a Cargo", 220, False),
        ("Curso", 200, False),
        ("Especialidad", 200, False),
        ("Contacto Institucional", 240, False),
    ]

    header_table = create_table_header(columnas)
    table_holder = ft.Container()
    info_holder = ft.Container()

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def docente_fila(item: dict, curso_nombre: str) -> ft.Container:
        profesor = profesores_por_legajo.get(item.get("legajo_profesor"))
        nombre_docente = item.get("profesor") or (
            f"{profesor.get('apellido', '')}, {profesor.get('nombre', '')}".strip(", ") if profesor else "-"
        )
        especialidad = _texto_seguro((profesor or {}).get("especialidad"))
        correo = (profesor or {}).get("correo_electronico")
        telefono = (profesor or {}).get("telefono")
        if correo and telefono:
            contacto = f"{correo} · {telefono}"
        else:
            contacto = _texto_seguro(correo or telefono)

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=220,
                        content=ft.Text(
                            item.get("materia", "-"),
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=220,
                        content=ft.Text(
                            f"Prof. {nombre_docente}" if nombre_docente and nombre_docente != "-" else "-",
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(width=200, content=ft.Text(curso_nombre, size=13, color=MUTED)),
                    ft.Container(width=200, content=ft.Text(especialidad, size=13, color=MUTED)),
                    ft.Container(width=240, content=ft.Text(contacto, size=13, color=TEAL)),
                ],
            ),
        )

    def visibles() -> list[dict]:
        hijo = hijo_seleccionado()
        filas = docentes_del_hijo(hijo)
        texto = (estado["texto"] or "").lower()
        if not texto:
            return filas
        filtradas = []
        for item in filas:
            profesor = profesores_por_legajo.get(item.get("legajo_profesor")) or {}
            contenido = " ".join(
                [
                    str(item.get("materia", "")),
                    str(item.get("profesor", "")),
                    str(profesor.get("nombre", "")),
                    str(profesor.get("apellido", "")),
                    str(profesor.get("especialidad", "")),
                ]
            ).lower()
            if texto in contenido:
                filtradas.append(item)
        return filtradas

    def render():
        hijo = hijo_seleccionado()
        curso = curso_de(hijo) if hijo else None
        nivel = nivel_de(hijo) if hijo else None
        curso_nombre = curso.get("nombre") if curso else "-"
        nivel_nombre = nivel.get("nombre") if nivel else "-"

        if hijo:
            info_holder.content = ft.Container(
                bgcolor=TEAL_LIGHT,
                border_radius=BORDER_RADIUS,
                padding=16,
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=TEAL),
                        ft.Text(
                            f"Docentes del alumno: {_nombre_completo(hijo)} · {curso_nombre} (Nivel {nivel_nombre})",
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ],
                ),
            )
        else:
            info_holder.content = ft.Container()

        filas = visibles()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[docente_fila(item, curso_nombre) for item in filas]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay materias asignadas para el curso de este alumno.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
            min_width=1080,
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["asignaciones"] = await api_client.get_asignaciones()
            estado["profesores"] = await api_client.get_profesores(solo_activos=False)
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la nómina docente: {err}")
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_cambiar_alumno(e):
        estado["legajo"] = int(alumno_dropdown.value) if alumno_dropdown.value else None
        render()

    async def on_refrescar(e):
        await recargar()

    search_field.on_change = on_buscar
    alumno_dropdown.on_change = on_cambiar_alumno
    btn_refrescar.on_click = on_refrescar

    render()

    return layout(
        [
            info_holder,
            filters_bar,
            aviso_error,
            table_holder,
        ]
    )
