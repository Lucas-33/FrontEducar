import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
    CARD_RADIUS,
    CONTROL_HEIGHT,
    MUTED,
    ORANGE,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)
from frontend.app.components.form_controls import status_badge
from frontend.app.components.table_view import (
    create_table_container,
    create_table_header,
)

ICONOS_NIVEL = {
    "inicial": ft.Icons.CHILD_CARE,
    "primario": ft.Icons.MENU_BOOK_OUTLINED,
    "secundario": ft.Icons.SCHOOL_OUTLINED,
}


async def get_admin_niveles_view(page: ft.Page) -> ft.Row:
    """Vista de configuración y control de Niveles Educativos conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    estado: dict = {"niveles": [], "cursos": [], "alumnos": []}

    try:
        estado["niveles"] = await api_client.get_niveles()
    except Exception:
        estado["niveles"] = []
    try:
        estado["cursos"] = await api_client.get_cursos()
    except Exception:
        estado["cursos"] = []
    try:
        estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
    except Exception:
        estado["alumnos"] = []

    def cursos_del_nivel(id_nivel: int) -> list[dict]:
        return [c for c in estado["cursos"] if c.get("id_nivel") == id_nivel]

    def matricula_del_nivel(id_nivel: int) -> int:
        ids_cursos = {c["id_curso"] for c in cursos_del_nivel(id_nivel)}
        return len(
            [
                a
                for a in estado["alumnos"]
                if a.get("id_curso") in ids_cursos
                and a.get("estado_alumno") == "ACTIVO"
            ]
        )

    # ==================== 1. TARJETAS DE NIVELES (KPIS RESUMEN) ====================
    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    def nivel_kpi_card(nivel: dict) -> ft.Container:
        nombre = nivel.get("nombre", "")
        icono = ICONOS_NIVEL.get(nombre.strip().lower(), ft.Icons.SCHOOL_OUTLINED)
        cursos_count = len(cursos_del_nivel(nivel["id_nivel"]))
        matricula = matricula_del_nivel(nivel["id_nivel"])

        return ft.Container(
            expand=True,
            bgcolor=BG_WHITE,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=CARD_RADIUS,
            padding=24,
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=42,
                                height=42,
                                bgcolor=TEAL_LIGHT,
                                border_radius=BORDER_RADIUS,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icono, size=22, color=TEAL_DARK),
                            ),
                            status_badge("Activo"),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                nombre,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=TEAL_DARK,
                            ),
                            ft.Text(
                                f"Código interno: {nivel['id_nivel']}",
                                size=12,
                                color=ORANGE,
                                weight=ft.FontWeight.W_600,
                            ),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1, thickness=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Cursos Activos:", size=12, color=MUTED),
                            ft.Text(
                                str(cursos_count),
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_COLOR,
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Matrícula Activa:", size=12, color=MUTED),
                            ft.Text(
                                str(matricula),
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_COLOR,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def render_cards() -> ft.Row:
        return ft.Row(
            spacing=20,
            controls=[nivel_kpi_card(n) for n in estado["niveles"]]
            or [
                ft.Text(
                    "No hay niveles educativos cargados todavía.",
                    size=13,
                    color=MUTED,
                )
            ],
        )

    tabla_niveles_holder = ft.Container()
    cards_holder = ft.Container()

    # ==================== 2. DETALLE DE NIVELES ====================
    columnas_niveles = [
        ("Código", 110, False),
        ("Nivel Institucional", 240, False),
        ("Cursos Activos", 160, False),
        ("Matrícula Activa", 160, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_niveles)

    def fila_acciones(al_editar, al_eliminar) -> ft.Container:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment(1, 0),
            content=ft.Row(
                spacing=6,
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_size=17,
                        icon_color=TEAL,
                        tooltip="Editar nivel",
                        padding=0,
                        on_click=al_editar,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=17,
                        icon_color=BADGE_RED_TXT,
                        tooltip="Eliminar nivel",
                        padding=0,
                        on_click=al_eliminar,
                    ),
                ],
            ),
        )

    def nivel_row(item: dict) -> ft.Container:
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
                            f"NIV-{item['id_nivel']}",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(
                        width=240,
                        content=ft.Text(
                            item["nombre"],
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=160,
                        content=ft.Text(
                            str(len(cursos_del_nivel(item["id_nivel"]))),
                            size=13,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=160,
                        content=ft.Text(
                            str(matricula_del_nivel(item["id_nivel"])),
                            size=13,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(width=100, content=status_badge("Activo")),
                    fila_acciones(
                        lambda e, n=item: abrir_editar_nivel(n),
                        lambda e, n=item: confirmar_eliminar_nivel(n),
                    ),
                ],
            ),
        )

    def render():
        cards_holder.content = render_cards()
        tabla_niveles_holder.content = create_table_container(
            header=header_table,
            rows=[nivel_row(n) for n in estado["niveles"]]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay niveles educativos cargados.", size=13, color=MUTED
                    ),
                )
            ],
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["niveles"] = await api_client.get_niveles()
            estado["cursos"] = await api_client.get_cursos()
            estado["alumnos"] = await api_client.get_alumnos(solo_activos=False)
        except Exception as err:
            aviso_error.value = f"⚠️ No se pudo refrescar la información: {err}"
            aviso_error.visible = True
        render()

    # ==================== 3. DIÁLOGO NUEVO NIVEL ====================
    btn_nuevo_nivel = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16, color=BG_WHITE),
                ft.Text(
                    "Nuevo Nivel", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
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

    def abrir_nuevo_nivel(e):
        nombre_field = ft.TextField(
            label="Nombre del nivel *", hint_text="Ej: Terciario", width=380
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar(e):
            nombre = (nombre_field.value or "").strip()
            if not nombre:
                error_text.value = "El nombre es obligatorio."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.create_nivel({"nombre": nombre})
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear el nivel."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                error_text.value = f"⚠️ {detalle}"
                error_text.visible = True
                error_text.update()
                return
            except httpx.RequestError:
                error_text.value = "⚠️ Error de conexión con el backend."
                error_text.visible = True
                error_text.update()
                return
            page.pop_dialog()
            await recargar()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Nivel Educativo", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14, width=380, tight=True, controls=[nombre_field, error_text]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Crear Nivel", bgcolor=TEAL, color=BG_WHITE, on_click=guardar
                ),
            ],
        )
        page.show_dialog(dlg)

    btn_nuevo_nivel.on_click = abrir_nuevo_nivel

    # ==================== 3b. DIÁLOGOS EDITAR / ELIMINAR NIVEL ====================
    def abrir_editar_nivel(nivel: dict):
        nombre_field = ft.TextField(
            label="Nombre del nivel *",
            value=nivel.get("nombre") or "",
            width=380,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def guardar_edicion(e):
            nombre = (nombre_field.value or "").strip()
            if not nombre:
                error_text.value = "El nombre es obligatorio."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.update_nivel(nivel["id_nivel"], {"nombre": nombre})
            except httpx.HTTPStatusError as err:
                detalle = "Error al actualizar el nivel."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                error_text.value = f"⚠️ {detalle}"
                error_text.visible = True
                error_text.update()
                return
            except httpx.RequestError:
                error_text.value = "⚠️ Error de conexión con el backend."
                error_text.visible = True
                error_text.update()
                return
            page.pop_dialog()
            await recargar()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Editar Nivel NIV-{nivel['id_nivel']}",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=14, width=380, tight=True, controls=[nombre_field, error_text]
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Guardar Cambios",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=guardar_edicion,
                ),
            ],
        )
        page.show_dialog(dlg)

    def confirmar_eliminar_nivel(nivel: dict):
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def eliminar(e):
            try:
                await api_client.delete_nivel(nivel["id_nivel"])
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo eliminar el nivel."
                try:
                    detalle = err.response.json().get("detail", detalle)
                except Exception:
                    pass
                error_text.value = f"⚠️ {detalle}"
                error_text.visible = True
                error_text.update()
                return
            except httpx.RequestError:
                error_text.value = "⚠️ Error de conexión con el backend."
                error_text.visible = True
                error_text.update()
                return
            page.pop_dialog()
            await recargar()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Eliminar Nivel Educativo", size=18, weight=ft.FontWeight.BOLD
            ),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        f"¿Confirma eliminar el nivel «{nivel.get('nombre')}»? "
                        "Solo es posible si no tiene cursos asociados.",
                        size=13,
                        color=TEXT_COLOR,
                    ),
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Eliminar", bgcolor=BADGE_RED_TXT, color=BG_WHITE, on_click=eliminar
                ),
            ],
        )
        page.show_dialog(dlg)

    render()

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Estructura Académica — Niveles Educativos K-12",
        active_route="/admin/niveles",
        content_controls=[
            aviso_error,
            cards_holder,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Detalle Pedagógico y Servicios por Nivel",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEAL_DARK,
                    ),
                    btn_nuevo_nivel,
                ],
            ),
            tabla_niveles_holder,
        ],
    )
