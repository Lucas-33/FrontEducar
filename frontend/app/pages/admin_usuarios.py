import flet as ft
import httpx

from frontend.app.api_client import api_client
from frontend.app.components.admin_layout import admin_layout
from frontend.app.components.constants import (
    BADGE_RED_TXT,
    BG_WHITE,
    BORDER_COLOR,
    BORDER_RADIUS,
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
    create_pagination_bar,
    create_table_container,
    create_table_header,
)

# Nombre legible para cada rol del backend
ROL_DISPLAY = {
    "ADMIN": "Administrador",
    "TEACHER": "Docente",
    "PARENT": "Padre / Tutor",
    "STUDENT": "Alumno",
}
ROL_API = {valor: clave for clave, valor in ROL_DISPLAY.items()}


def _fecha_corta(iso: str | None) -> str:
    """Convierte un ISO timestamp del backend en dd/mm/aaaa."""
    if not iso or len(iso) < 10:
        return "-"
    return f"{iso[8:10]}/{iso[5:7]}/{iso[0:4]}"


async def get_admin_usuarios_view(page: ft.Page) -> ft.Row:
    """Vista de Usuarios, Control de Acceso RBAC conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and not api_client.token:
        api_client.set_token(token_almacenado)

    # ==================== ESTADO DE LA VISTA ====================
    estado: dict = {
        "usuarios": [],
        "roles": [],
        "texto": "",
        "rol": "Todos",
        "activo": "Todos",
    }

    try:
        estado["usuarios"] = await api_client.get_usuarios()
    except Exception:
        estado["usuarios"] = []

    try:
        estado["roles"] = await api_client.get_roles()
    except Exception:
        estado["roles"] = []

    # ==================== 1. FILTROS Y ACCIÓN ====================
    search_field = ft.TextField(
        hint_text="Buscar usuario o vínculo...",
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

    def crear_filtro_dropdown(
        hint: str, width: int, opciones: list[str]
    ) -> ft.Container:
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

    filtro_rol_container = crear_filtro_dropdown(
        "Rol: Todos",
        150,
        ["Todos", "Administrador", "Docente", "Padre / Tutor", "Alumno"],
    )
    filtro_estado_container = crear_filtro_dropdown(
        "Estado: Todos", 140, ["Todos", "Activo", "Inactivo"]
    )
    filtro_rol_dropdown: ft.Dropdown = filtro_rol_container.content
    filtro_estado_dropdown: ft.Dropdown = filtro_estado_container.content

    btn_nuevo_usuario = ft.Button(
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.PERSON_ADD_ALT_1_OUTLINED, size=16, color=BG_WHITE),
                ft.Text(
                    "Nuevo Usuario", size=14, weight=ft.FontWeight.W_600, color=BG_WHITE
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
                controls=[search_input, filtro_rol_container, filtro_estado_container],
            ),
            btn_nuevo_usuario,
        ],
    )

    aviso_error = ft.Text(
        "", size=13, weight=ft.FontWeight.W_600, color=BADGE_RED_TXT, visible=False
    )

    # ==================== 2. TABLA DE USUARIOS Y ROLES ====================
    columnas_usuarios = [
        ("Usuario", 200, False),
        ("Rol Asignado", 140, False),
        ("Vinculación / Perfil", 260, False),
        ("Alta", 110, False),
        ("Estado", 100, False),
        ("Acciones", None, True),
    ]

    header_table = create_table_header(columnas_usuarios)
    table_holder = ft.Container()
    pagination_holder = ft.Container()

    def rol_badge(rol: str) -> ft.Container:
        colores = {
            "Administrador": (TEAL_DARK, BG_WHITE),
            "Docente": (TEAL_LIGHT, TEAL_DARK),
            "Padre / Tutor": ("#FFF3E7", ORANGE),
            "Alumno": ("#EBFEE6", "#10B981"),
        }
        bg, color = colores.get(rol, (TEAL_LIGHT, TEAL_DARK))
        return ft.Container(
            padding=ft.Padding(8, 3, 8, 3),
            bgcolor=bg,
            border_radius=4,
            content=ft.Text(rol, size=11, weight=ft.FontWeight.BOLD, color=color),
        )

    def mostrar_error(mensaje: str):
        aviso_error.value = f"⚠️ {mensaje}"
        aviso_error.visible = True
        try:
            page.update()
        except Exception:
            pass

    def abrir_reset_password(usuario: dict):
        password_field = ft.TextField(
            label="Nueva contraseña",
            password=True,
            can_reveal_password=True,
            width=380,
        )
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        async def confirmar(e):
            nueva = (password_field.value or "").strip()
            if len(nueva) < 6:
                error_text.value = "La contraseña debe tener al menos 6 caracteres."
                error_text.visible = True
                error_text.update()
                return
            try:
                await api_client.update_usuario(
                    usuario["id_usuario"], {"password": nueva}
                )
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo actualizar la contraseña."
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
                f"Restablecer contraseña — {usuario['username']}",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=12,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        "La contraseña anterior dejará de funcionar.",
                        size=13,
                        color=MUTED,
                    ),
                    password_field,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Guardar", bgcolor=TEAL, color=BG_WHITE, on_click=confirmar),
            ],
        )
        page.show_dialog(dlg)

    def usuario_row(item: dict) -> ft.Container:
        rol_legible = ROL_DISPLAY.get(item.get("rol", ""), item.get("rol", "-"))
        activo = bool(item.get("activo", True))

        async def toggle_estado(e):
            try:
                await api_client.update_usuario(
                    item["id_usuario"], {"activo": not activo}
                )
            except Exception as err:
                mostrar_error(
                    f"No se pudo cambiar el estado de '{item['username']}': {err}"
                )
                return
            await recargar()

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            item["username"],
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=TEAL_DARK,
                        ),
                    ),
                    ft.Container(width=140, content=rol_badge(rol_legible)),
                    ft.Container(
                        width=260,
                        content=ft.Text(
                            item.get("vinculacion", "-"), size=13, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=110,
                        content=ft.Text(
                            _fecha_corta(item.get("creado_en")), size=12, color=MUTED
                        ),
                    ),
                    ft.Container(
                        width=100,
                        content=status_badge("Activo" if activo else "Bloqueado"),
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=12,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.KEY_OUTLINED,
                                    icon_size=16,
                                    icon_color=TEAL,
                                    tooltip="Restablecer Contraseña",
                                    padding=0,
                                    on_click=lambda e, u=item: abrir_reset_password(u),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.LOCK_OPEN_OUTLINED
                                    if not activo
                                    else ft.Icons.BLOCK_OUTLINED,
                                    icon_size=16,
                                    icon_color="#10B981"
                                    if not activo
                                    else BADGE_RED_TXT,
                                    tooltip="Reactivar Acceso"
                                    if not activo
                                    else "Bloquear Acceso",
                                    padding=0,
                                    on_click=toggle_estado,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def usuarios_filtrados() -> list[dict]:
        texto = (estado["texto"] or "").lower()
        resultado = []
        for u in estado["usuarios"]:
            rol_legible = ROL_DISPLAY.get(u.get("rol", ""), "")
            activo_legible = "Activo" if u.get("activo") else "Inactivo"
            if estado["rol"] != "Todos" and rol_legible != estado["rol"]:
                continue
            if estado["activo"] != "Todos" and activo_legible != estado["activo"]:
                continue
            if (
                texto
                and texto
                not in f"{u.get('username', '')} {u.get('vinculacion', '')}".lower()
            ):
                continue
            resultado.append(u)
        return resultado

    def render():
        visibles = usuarios_filtrados()
        table_holder.content = create_table_container(
            header=header_table,
            rows=[usuario_row(u) for u in visibles]
            or [
                ft.Container(
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "No hay usuarios que coincidan con los filtros.",
                        size=13,
                        color=MUTED,
                    ),
                )
            ],
        )
        pagination_holder.content = create_pagination_bar(
            texto_info=f"Mostrando {len(visibles)} de {len(estado['usuarios'])} cuentas registradas",
            pagina_actual=1,
            total_paginas=max(1, (len(visibles) + 9) // 10),
        )
        try:
            page.update()
        except Exception:
            pass

    async def recargar():
        try:
            estado["usuarios"] = await api_client.get_usuarios()
        except Exception as err:
            mostrar_error(f"No se pudo refrescar la lista de usuarios: {err}")
        render()

    def on_buscar(e):
        estado["texto"] = search_field.value or ""
        render()

    def on_filtrar_rol(e):
        estado["rol"] = filtro_rol_dropdown.value or "Todos"
        render()

    def on_filtrar_estado(e):
        estado["activo"] = filtro_estado_dropdown.value or "Todos"
        render()

    search_field.on_change = on_buscar
    filtro_rol_dropdown.on_change = on_filtrar_rol
    filtro_estado_dropdown.on_change = on_filtrar_estado

    # ==================== 3. DIÁLOGO NUEVO USUARIO ====================
    async def abrir_nuevo_usuario(e):
        try:
            alumnos = await api_client.get_alumnos(solo_activos=True)
        except Exception:
            alumnos = []
        try:
            profesores = await api_client.get_profesores(solo_activos=True)
        except Exception:
            profesores = []
        try:
            padres = await api_client.get_padres()
        except Exception:
            padres = []

        ids_rol = {r.get("nombre"): r.get("id_rol") for r in estado["roles"]}

        username_field = ft.TextField(
            label="Usuario *", hint_text="ej: jperez", width=380
        )
        password_field = ft.TextField(
            label="Contraseña *", password=True, can_reveal_password=True, width=380
        )
        rol_field = ft.Dropdown(
            label="Rol *",
            value="Alumno",
            width=380,
            options=[
                ft.dropdown.Option(r)
                for r in ["Administrador", "Docente", "Padre / Tutor", "Alumno"]
            ],
        )
        vinculo_field = ft.Dropdown(label="Vincular a", width=380, options=[])
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        def opciones_vinculo(rol_legible: str) -> list[ft.dropdown.Option]:
            sin_vinculo = ft.dropdown.Option(key="", text="Sin vínculo")
            if rol_legible == "Docente":
                return [sin_vinculo] + [
                    ft.dropdown.Option(
                        key=f"profesor:{p['legajo']}",
                        text=f"{p['apellido']}, {p['nombre']} (#{p['legajo']})",
                    )
                    for p in profesores
                ]
            if rol_legible == "Padre / Tutor":
                return [sin_vinculo] + [
                    ft.dropdown.Option(
                        key=f"padre:{p['id_padre']}",
                        text=f"{p['apellido']}, {p['nombre']} (DNI {p['dni']})",
                    )
                    for p in padres
                ]
            if rol_legible == "Alumno":
                return [sin_vinculo] + [
                    ft.dropdown.Option(
                        key=f"alumno:{a['legajo']}",
                        text=f"{a['apellido']}, {a['nombre']} (#{a['legajo']})",
                    )
                    for a in alumnos
                ]
            return [sin_vinculo]

        def on_rol_change(e):
            vinculo_field.options = opciones_vinculo(rol_field.value or "")
            vinculo_field.value = ""
            vinculo_field.update()

        rol_field.on_change = on_rol_change
        vinculo_field.options = opciones_vinculo(rol_field.value or "")

        async def guardar(e):
            username = (username_field.value or "").strip()
            password = (password_field.value or "").strip()
            rol_legible = rol_field.value or ""

            if not username or not password:
                error_text.value = "Usuario y contraseña son obligatorios."
                error_text.visible = True
                error_text.update()
                return

            id_rol = ids_rol.get(ROL_API.get(rol_legible, ""))
            if not id_rol:
                error_text.value = "No se pudo resolver el rol seleccionado."
                error_text.visible = True
                error_text.update()
                return

            payload: dict = {
                "username": username,
                "password": password,
                "id_rol": id_rol,
                "activo": True,
            }

            vinculo = vinculo_field.value or ""
            if vinculo:
                tipo, ident = vinculo.split(":", 1)
                if tipo == "alumno":
                    payload["legajo_alumno"] = int(ident)
                elif tipo == "profesor":
                    payload["legajo_profesor"] = int(ident)
                elif tipo == "padre":
                    payload["id_padre"] = int(ident)

            try:
                await api_client.create_usuario(payload)
            except httpx.HTTPStatusError as err:
                detalle = "Error al crear el usuario."
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
            title=ft.Text("Nuevo Usuario", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=380,
                tight=True,
                controls=[
                    ft.Text(
                        "Cree la cuenta y vincúlela a un alumno, docente o tutor si corresponde.",
                        size=13,
                        color=MUTED,
                    ),
                    username_field,
                    password_field,
                    rol_field,
                    vinculo_field,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "Crear Usuario", bgcolor=TEAL, color=BG_WHITE, on_click=guardar
                ),
            ],
        )
        page.show_dialog(dlg)

    btn_nuevo_usuario.on_click = abrir_nuevo_usuario

    aviso_seguridad = ft.Container(
        bgcolor=TEAL_LIGHT,
        border_radius=BORDER_RADIUS,
        padding=14,
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.LOCK_OUTLINE, size=18, color=TEAL),
                ft.Text(
                    "Seguridad y Privacidad: Cada rol accede únicamente a las secciones autorizadas. Los padres solo pueden consultar y gestionar información de sus propios hijos vinculados.",
                    size=13,
                    color=TEAL_DARK,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
    )

    render()

    # ==================== 4. RETORNO CON ADMIN_LAYOUT ====================
    return admin_layout(
        page=page,
        titulo="Control de Acceso, Usuarios y Permisos RBAC",
        active_route="/admin/usuarios",
        content_controls=[
            aviso_seguridad,
            aviso_error,
            filters_bar,
            table_holder,
            pagination_holder,
        ],
    )
