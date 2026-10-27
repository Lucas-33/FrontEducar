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


def _crear_selector_alumnos_tutor(alumnos: list[dict]):
    """Crea una lista buscable con selección múltiple de alumnos.

    Devuelve el panel, el set de legajos seleccionados y dos helpers:
    ``establecer(legajos)`` para precargar la selección y ``render()`` para
    refrescar la lista cuando cambia el buscador.
    """
    seleccionados: set[int] = set()

    busqueda_field = ft.TextField(
        hint_text="Buscar por legajo, DNI, nombre o apellido...",
        hint_style=ft.TextStyle(size=12, color=MUTED),
        text_size=12,
        color=TEXT_COLOR,
        height=40,
        content_padding=ft.Padding(10, 0, 10, 0),
        prefix_icon=ft.Icons.SEARCH,
        border=ft.InputBorder.OUTLINE,
        border_color=BORDER_COLOR,
        focused_border_color=TEAL,
        border_radius=BORDER_RADIUS,
        bgcolor=BG_WHITE,
    )

    lista_view = ft.ListView(spacing=0, padding=0, height=190)
    contador_text = ft.Text("0 alumnos seleccionados", size=11, color=MUTED)

    def actualizar_contador():
        cantidad = len(seleccionados)
        contador_text.value = (
            f"{cantidad} alumno{'s' if cantidad != 1 else ''} seleccionado"
            f"{'s' if cantidad != 1 else ''}"
        )
        try:
            contador_text.update()
        except Exception:
            pass

    def alternar(e, legajo: int):
        if e.control.value:
            seleccionados.add(legajo)
        else:
            seleccionados.discard(legajo)
        actualizar_contador()

    def render():
        texto = (busqueda_field.value or "").strip().lower()
        filtrados = alumnos
        if texto:
            filtrados = [
                alumno
                for alumno in alumnos
                if texto
                in (
                    f"{alumno.get('legajo', '')} {alumno.get('dni', '')} "
                    f"{alumno.get('apellido', '')} {alumno.get('nombre', '')}"
                ).lower()
            ]

        filas: list[ft.Control] = []
        for alumno in filtrados:
            try:
                legajo = int(alumno.get("legajo"))
            except (TypeError, ValueError):
                continue
            filas.append(
                ft.Checkbox(
                    label=(
                        f"#{legajo} · {alumno.get('apellido', '')}, "
                        f"{alumno.get('nombre', '')} · DNI {alumno.get('dni', '')}"
                    ),
                    value=legajo in seleccionados,
                    label_style=ft.TextStyle(size=12, color=TEXT_COLOR),
                    on_change=lambda e, leg=legajo: alternar(e, leg),
                )
            )

        if not filas:
            filas.append(
                ft.Container(
                    padding=ft.Padding(8, 12, 8, 12),
                    content=ft.Text(
                        "No se encontraron alumnos con ese criterio.",
                        size=12,
                        color=MUTED,
                    ),
                )
            )

        lista_view.controls = filas
        try:
            lista_view.update()
        except Exception:
            pass
        actualizar_contador()

    def establecer(legajos):
        seleccionados.clear()
        for legajo in legajos or []:
            try:
                seleccionados.add(int(legajo))
            except (TypeError, ValueError):
                continue
        busqueda_field.value = ""
        try:
            busqueda_field.update()
        except Exception:
            pass
        render()

    busqueda_field.on_change = lambda e: render()

    panel = ft.Container(
        visible=False,
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Text(
                    "Alumnos a cargo",
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=TEXT_COLOR,
                ),
                ft.Text(
                    "Seleccione uno o más alumnos a cargo del tutor.",
                    size=11,
                    color=MUTED,
                ),
                busqueda_field,
                ft.Container(
                    height=190,
                    bgcolor=BG_WHITE,
                    border=ft.Border.all(1, BORDER_COLOR),
                    border_radius=BORDER_RADIUS,
                    padding=ft.Padding(8, 4, 8, 4),
                    content=lista_view,
                ),
                contador_text,
            ],
        ),
    )

    render()
    return panel, seleccionados, establecer, render


def _crear_panel_datos_tutor() -> tuple[ft.Container, dict[str, ft.TextField]]:
    """Crea los campos para dar de alta al tutor junto con su usuario."""

    def campo(
        label: str,
        hint: str,
        *,
        keyboard_type: ft.KeyboardType | None = None,
        regex: str | None = None,
    ) -> ft.TextField:
        extras: dict = {}
        if keyboard_type is not None:
            extras["keyboard_type"] = keyboard_type
        if regex is not None:
            extras["input_filter"] = ft.InputFilter(allow=True, regex_string=regex)
        return ft.TextField(
            label=label,
            hint_text=hint,
            hint_style=ft.TextStyle(size=12, color=MUTED),
            text_size=13,
            color=TEXT_COLOR,
            height=46,
            content_padding=ft.Padding(10, 8, 10, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            border_radius=BORDER_RADIUS,
            bgcolor=BG_WHITE,
            expand=True,
            **extras,
        )

    campos = {
        "dni": campo(
            "DNI *",
            "Ej: 30111222",
            keyboard_type=ft.KeyboardType.NUMBER,
            regex=r"^[0-9]*$",
        ),
        "nombre": campo("Nombre *", "Ej: Laura", keyboard_type=ft.KeyboardType.NAME),
        "apellido": campo(
            "Apellido *", "Ej: Gómez", keyboard_type=ft.KeyboardType.NAME
        ),
        "telefono": campo(
            "Teléfono",
            "Ej: 3624000000",
            keyboard_type=ft.KeyboardType.PHONE,
            regex=r"^[0-9\-\+\s]*$",
        ),
        "correo_electronico": campo(
            "Correo", "tutor@correo.com", keyboard_type=ft.KeyboardType.EMAIL
        ),
    }

    panel = ft.Container(
        visible=False,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(
                    "Datos del tutor",
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=TEXT_COLOR,
                ),
                ft.Text(
                    "Se dará de alta el tutor y se creará su usuario de acceso.",
                    size=11,
                    color=MUTED,
                ),
                ft.Row(spacing=10, controls=[campos["dni"], campos["nombre"]]),
                ft.Row(spacing=10, controls=[campos["apellido"], campos["telefono"]]),
                ft.Row(spacing=10, controls=[campos["correo_electronico"]]),
            ],
        ),
    )
    return panel, campos


def _leer_datos_tutor(campos: dict[str, ft.TextField]) -> dict:
    """Valida y devuelve los datos del tutor cargados en el formulario."""
    dni = (campos["dni"].value or "").strip()
    nombre = (campos["nombre"].value or "").strip()
    apellido = (campos["apellido"].value or "").strip()
    if not all([dni, nombre, apellido]):
        raise ValueError("DNI, nombre y apellido del tutor son obligatorios.")
    return {
        "dni": dni,
        "nombre": nombre,
        "apellido": apellido,
        "telefono": (campos["telefono"].value or "").strip() or None,
        "correo_electronico": (campos["correo_electronico"].value or "").strip()
        or None,
    }


def _precargar_datos_tutor(campos: dict[str, ft.TextField], tutor: dict | None) -> None:
    """Completa o limpia los campos del tutor."""
    datos = tutor or {}
    valores = {
        "dni": datos.get("dni", ""),
        "nombre": datos.get("nombre", ""),
        "apellido": datos.get("apellido", ""),
        "telefono": datos.get("telefono") or "",
        "correo_electronico": datos.get("correo_electronico") or "",
    }
    for clave, valor in valores.items():
        campos[clave].value = str(valor)


async def get_admin_usuarios_view(page: ft.Page) -> ft.Row:
    """Vista de Usuarios, Control de Acceso RBAC conectada a la API."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
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
        ("Usuario de acceso", 200, False),
        ("Rol Asignado", 140, False),
        ("Vinculación / Perfil", 260, False),
        ("Alta", 110, False),
        ("Estado", 100, False),
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

            # El token en memoria puede haberse perdido si el backend se reinició.
            token = getattr(page, "auth_token", None)
            if token and api_client.token != token:
                api_client.set_token(token)

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
            page.show_dialog(
                ft.SnackBar(
                    ft.Text(
                        f"Contraseña de '{usuario['username']}' actualizada. "
                        "La nueva clave ya está activa.",
                        color="white",
                    ),
                    bgcolor=TEAL,
                )
            )

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

    async def abrir_editar_usuario(usuario: dict):
        """Permite ver/editar el usuario de acceso, el rol y su vínculo."""
        try:
            alumnos = await api_client.get_todos_los_alumnos(solo_activos=False)
        except Exception:
            alumnos = []
        try:
            profesores = await api_client.get_profesores(solo_activos=False)
        except Exception:
            profesores = []
        try:
            padres = await api_client.get_todos_los_padres()
        except Exception:
            padres = []

        ids_rol = {r.get("nombre"): r.get("id_rol") for r in estado["roles"]}
        rol_actual = ROL_DISPLAY.get(
            usuario.get("rol", ""), usuario.get("rol", "Alumno")
        )

        padre_actual = next(
            (p for p in padres if p.get("id_padre") == usuario.get("id_padre")),
            None,
        )
        es_tutor_actual = rol_actual == "Padre / Tutor"

        vinculo_actual = ""
        if usuario.get("legajo_alumno"):
            vinculo_actual = f"alumno:{usuario['legajo_alumno']}"
        elif usuario.get("legajo_profesor"):
            vinculo_actual = f"profesor:{usuario['legajo_profesor']}"

        username_field = ft.TextField(
            label="Usuario / correo de acceso *",
            value=usuario.get("username", ""),
            width=520,
        )
        rol_field = ft.Dropdown(
            label="Rol *",
            value=rol_actual,
            width=520,
            options=[
                ft.dropdown.Option(r)
                for r in ["Administrador", "Docente", "Padre / Tutor", "Alumno"]
            ],
        )
        vinculo_field = ft.Dropdown(label="Vincular a", width=520, options=[])
        vinculo_field.visible = not es_tutor_actual
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        panel_tutor, campos_tutor = _crear_panel_datos_tutor()
        panel_tutor.visible = es_tutor_actual
        _precargar_datos_tutor(campos_tutor, padre_actual)

        panel_alumnos, alumnos_seleccionados, establecer_alumnos, _ = (
            _crear_selector_alumnos_tutor(alumnos)
        )
        panel_alumnos.visible = es_tutor_actual

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
            es_tutor = rol_field.value == "Padre / Tutor"
            vinculo_field.options = opciones_vinculo(rol_field.value or "")
            vinculo_field.value = ""
            vinculo_field.visible = not es_tutor
            panel_tutor.visible = es_tutor
            panel_alumnos.visible = es_tutor
            _precargar_datos_tutor(campos_tutor, padre_actual if es_tutor else None)
            establecer_alumnos([])
            try:
                page.update()
            except Exception:
                pass

        rol_field.on_select = on_rol_change
        vinculo_field.options = opciones_vinculo(rol_field.value or "")
        claves = {opc.key for opc in vinculo_field.options}
        vinculo_field.value = vinculo_actual if vinculo_actual in claves else ""

        vinculados_iniciales = usuario.get("alumnos_vinculados") or []
        if not vinculados_iniciales and usuario.get("id_padre"):
            try:
                hijos = await api_client.get_hijos(usuario["id_padre"])
                vinculados_iniciales = [
                    hijo.get("legajo") for hijo in hijos if hijo.get("legajo")
                ]
            except Exception:
                vinculados_iniciales = []
        establecer_alumnos(vinculados_iniciales)

        async def guardar(e):
            username = (username_field.value or "").strip()
            rol_legible = rol_field.value or ""

            if not username:
                error_text.value = "El usuario / correo de acceso es obligatorio."
                error_text.visible = True
                error_text.update()
                return

            id_rol = ids_rol.get(ROL_API.get(rol_legible, ""))
            if not id_rol:
                error_text.value = "No se pudo resolver el rol seleccionado."
                error_text.visible = True
                error_text.update()
                return

            payload: dict = {"username": username, "id_rol": id_rol}

            if rol_legible == "Padre / Tutor":
                try:
                    payload["tutor"] = _leer_datos_tutor(campos_tutor)
                except ValueError as exc:
                    error_text.value = f"⚠️ {exc}"
                    error_text.visible = True
                    error_text.update()
                    return
                payload["legajos_alumnos"] = sorted(alumnos_seleccionados)
            else:
                payload.update(
                    {
                        "legajo_alumno": None,
                        "legajo_profesor": None,
                        "id_padre": None,
                    }
                )
                vinculo = vinculo_field.value or ""
                if vinculo:
                    tipo, ident = vinculo.split(":", 1)
                    if tipo == "alumno":
                        payload["legajo_alumno"] = int(ident)
                    elif tipo == "profesor":
                        payload["legajo_profesor"] = int(ident)

            # El token en memoria puede haberse perdido si el backend se reinició.
            token = getattr(page, "auth_token", None)
            if token and api_client.token != token:
                api_client.set_token(token)

            try:
                await api_client.update_usuario(usuario["id_usuario"], payload)
            except httpx.HTTPStatusError as err:
                detalle = "No se pudo actualizar el usuario."
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
            detalle_vinculo = ""
            if rol_legible == "Padre / Tutor" and alumnos_seleccionados:
                cantidad = len(alumnos_seleccionados)
                detalle_vinculo = (
                    f" {cantidad} alumno{'s' if cantidad != 1 else ''} vinculado"
                    f"{'s' if cantidad != 1 else ''}."
                )
            page.show_dialog(
                ft.SnackBar(
                    ft.Text(
                        f"Usuario '{username}' actualizado correctamente."
                        f"{detalle_vinculo}",
                        color="white",
                    ),
                    bgcolor=TEAL,
                )
            )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Editar usuario — {usuario['username']}",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            content=ft.Column(
                spacing=14,
                width=520,
                tight=True,
                controls=[
                    ft.Text(
                        "Cambie el usuario de acceso, el rol o los datos del tutor. "
                        "Si el rol es Padre / Tutor complete sus datos y seleccione "
                        "uno o más alumnos a cargo.",
                        size=13,
                        color=MUTED,
                    ),
                    username_field,
                    rol_field,
                    vinculo_field,
                    panel_tutor,
                    panel_alumnos,
                    error_text,
                ],
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
                ft.Button("Guardar", bgcolor=TEAL, color=BG_WHITE, on_click=guardar),
            ],
        )
        page.show_dialog(dlg)

    def boton_accion(
        texto: str,
        icono: ft.IconData,
        color: str,
        on_click,
    ) -> ft.Button:
        return ft.Button(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(icono, size=18, color=BG_WHITE),
                    ft.Text(
                        texto,
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=BG_WHITE,
                    ),
                ],
            ),
            bgcolor=color,
            width=300,
            height=CONTROL_HEIGHT,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
            on_click=on_click,
        )

    def abrir_panel_acciones(usuario: dict):
        activo = bool(usuario.get("activo", True))
        rol_legible = ROL_DISPLAY.get(usuario.get("rol", ""), usuario.get("rol", "-"))

        async def editar_usuario(e):
            page.pop_dialog()
            await abrir_editar_usuario(usuario)

        async def alternar_estado(e):
            # El token en memoria puede haberse perdido si el backend se reinició.
            token = getattr(page, "auth_token", None)
            if token and api_client.token != token:
                api_client.set_token(token)
            try:
                await api_client.update_usuario(
                    usuario["id_usuario"], {"activo": not activo}
                )
            except Exception as err:
                mostrar_error(
                    f"No se pudo cambiar el estado de '{usuario['username']}': {err}"
                )
                return

            page.pop_dialog()
            await recargar()
            page.show_dialog(
                ft.SnackBar(
                    ft.Text(
                        f"Acceso de '{usuario['username']}' "
                        f"{'bloqueado' if activo else 'reactivado'}.",
                        color="white",
                    ),
                    bgcolor=TEAL,
                )
            )

        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text(
                f"Usuario: {usuario['username']}",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=TEAL_DARK,
            ),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        f"Usuario / correo de acceso: {usuario.get('username', '-')}",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=TEXT_COLOR,
                    ),
                    ft.Text(f"Rol: {rol_legible}", size=13, color=TEXT_COLOR),
                    ft.Text(
                        f"Vinculación: {usuario.get('vinculacion', '-')}",
                        size=13,
                        color=MUTED,
                    ),
                    ft.Text(
                        f"Estado actual: {'Activo' if activo else 'Bloqueado'}",
                        size=13,
                        color=MUTED,
                    ),
                    boton_accion(
                        "Editar usuario / vínculo",
                        ft.Icons.EDIT_OUTLINED,
                        TEAL_DARK,
                        editar_usuario,
                    ),
                    boton_accion(
                        "Restablecer contraseña",
                        ft.Icons.KEY_OUTLINED,
                        TEAL,
                        lambda e: (
                            page.pop_dialog(),
                            abrir_reset_password(usuario),
                        ),
                    ),
                    boton_accion(
                        "Reactivar acceso" if not activo else "Bloquear acceso",
                        ft.Icons.LOCK_OPEN_OUTLINED
                        if not activo
                        else ft.Icons.BLOCK_OUTLINED,
                        "#10B981" if not activo else BADGE_RED_TXT,
                        alternar_estado,
                    ),
                ],
            ),
            actions=[ft.TextButton("Cancelar", on_click=lambda _: page.pop_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    def usuario_row(item: dict) -> ft.Container:
        rol_legible = ROL_DISPLAY.get(item.get("rol", ""), item.get("rol", "-"))
        activo = bool(item.get("activo", True))

        return ft.Container(
            height=54,
            padding=ft.Padding(16, 0, 16, 0),
            border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
            ink=True,
            tooltip="Haga clic para gestionar este usuario",
            on_click=lambda e, u=item: abrir_panel_acciones(u),
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
            texto_info=(
                f"Mostrando {len(visibles)} de {len(estado['usuarios'])} cuentas "
                "registradas · Haga clic en una fila para gestionarla"
            ),
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
    filtro_rol_dropdown.on_select = on_filtrar_rol
    filtro_estado_dropdown.on_select = on_filtrar_estado

    # ==================== 3. DIÁLOGO NUEVO USUARIO ====================
    async def abrir_nuevo_usuario(e):
        try:
            alumnos = await api_client.get_todos_los_alumnos(solo_activos=False)
        except Exception:
            alumnos = []
        try:
            profesores = await api_client.get_profesores(solo_activos=True)
        except Exception:
            profesores = []

        ids_rol = {r.get("nombre"): r.get("id_rol") for r in estado["roles"]}

        username_field = ft.TextField(
            label="Usuario *", hint_text="ej: jperez", width=520
        )
        password_field = ft.TextField(
            label="Contraseña *", password=True, can_reveal_password=True, width=520
        )
        rol_field = ft.Dropdown(
            label="Rol *",
            value="Alumno",
            width=520,
            options=[
                ft.dropdown.Option(r)
                for r in ["Administrador", "Docente", "Padre / Tutor", "Alumno"]
            ],
        )
        vinculo_field = ft.Dropdown(label="Vincular a", width=520, options=[])
        error_text = ft.Text("", size=12, color=BADGE_RED_TXT, visible=False)

        panel_tutor, campos_tutor = _crear_panel_datos_tutor()
        panel_alumnos, alumnos_seleccionados, establecer_alumnos, _ = (
            _crear_selector_alumnos_tutor(alumnos)
        )

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
            es_tutor = rol_field.value == "Padre / Tutor"
            vinculo_field.options = opciones_vinculo(rol_field.value or "")
            vinculo_field.value = ""
            vinculo_field.visible = not es_tutor
            panel_tutor.visible = es_tutor
            panel_alumnos.visible = es_tutor
            _precargar_datos_tutor(campos_tutor, None)
            establecer_alumnos([])
            try:
                page.update()
            except Exception:
                pass

        rol_field.on_select = on_rol_change
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

            if rol_legible == "Padre / Tutor":
                if not alumnos_seleccionados:
                    error_text.value = (
                        "⚠️ Seleccione al menos un alumno a cargo del tutor."
                    )
                    error_text.visible = True
                    error_text.update()
                    return
                try:
                    payload["tutor"] = _leer_datos_tutor(campos_tutor)
                except ValueError as exc:
                    error_text.value = f"⚠️ {exc}"
                    error_text.visible = True
                    error_text.update()
                    return
                payload["legajos_alumnos"] = sorted(alumnos_seleccionados)
            else:
                vinculo = vinculo_field.value or ""
                if vinculo:
                    tipo, ident = vinculo.split(":", 1)
                    if tipo == "alumno":
                        payload["legajo_alumno"] = int(ident)
                    elif tipo == "profesor":
                        payload["legajo_profesor"] = int(ident)

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
            detalle_vinculo = ""
            if rol_legible == "Padre / Tutor" and alumnos_seleccionados:
                cantidad = len(alumnos_seleccionados)
                detalle_vinculo = (
                    f" {cantidad} alumno{'s' if cantidad != 1 else ''} vinculado"
                    f"{'s' if cantidad != 1 else ''}."
                )
            page.show_dialog(
                ft.SnackBar(
                    ft.Text(
                        f"Usuario '{username}' creado correctamente.{detalle_vinculo}",
                        color="white",
                    ),
                    bgcolor=TEAL,
                )
            )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Usuario", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                spacing=14,
                width=520,
                tight=True,
                controls=[
                    ft.Text(
                        "Cree la cuenta de acceso. Si el rol es Padre / Tutor, "
                        "complete los datos del tutor y seleccione uno o más "
                        "alumnos a cargo: se crearán el tutor y el usuario juntos.",
                        size=13,
                        color=MUTED,
                    ),
                    username_field,
                    password_field,
                    rol_field,
                    vinculo_field,
                    panel_tutor,
                    panel_alumnos,
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
