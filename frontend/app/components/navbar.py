import flet as ft

from frontend.app.components.constants import (
    BG_WHITE,
    BORDER_COLOR,
    MUTED,
    TEAL,
    TEAL_DARK,
    TEAL_LIGHT,
    TEXT_COLOR,
)


def create_navbar(page: ft.Page, active_route: str = "/") -> ft.Container:
    def navegar(ruta: str):
        page.run_task(page.push_route, ruta)

    # ==================== 1. COMPONENTES COMPARTIDOS ====================
    btn_portal = ft.Button(
        "PORTAL",
        icon=ft.Icons.LOGIN,
        bgcolor=TEAL_LIGHT,
        color=TEAL_DARK,
        elevation=0,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=lambda _: navegar("/portal"),
    )

    logo_area = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.CLICK,
        on_tap=lambda _: navegar("/"),
        content=ft.Row(
            spacing=10,
            controls=[
                ft.Container(
                    width=38, height=38, bgcolor=TEAL, border_radius=19,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(ft.Icons.SCHOOL, color="white", size=20)
                ),
                ft.Column(
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Educar SGE", weight=ft.FontWeight.BOLD, size=18, color=TEAL_DARK),
                        ft.Text("INSTITUTO EDUCATIVO", size=10, color=MUTED),
                    ]
                )
            ]
        )
    )

    # ==================== 2. DISEÑO ESCRITORIO (PC) ====================
    def desktop_link(texto: str, ruta: str):
        es_activo = active_route == ruta
        # CORRECCIÓN: Usamos content=ft.Text() en lugar de text="" para tu versión de Flet
        return ft.TextButton(
            content=ft.Text(
                texto, 
                size=14, 
                weight=ft.FontWeight.W_600 if es_activo else ft.FontWeight.W_500
            ),
            style=ft.ButtonStyle(
                color=TEAL if es_activo else TEXT_COLOR,
                overlay_color="transparent",
            ),
            on_click=lambda _: navegar(ruta)
        )

    derecha_desktop = ft.Row(
        spacing=16,
        controls=[
            desktop_link("Inicio", "/"),
            desktop_link("Quiénes Somos", "/quienes-somos"),
            desktop_link("Niveles", "/niveles"),
            desktop_link("Inscripción", "/inscripcion"),
            desktop_link("Contacto", "/contacto"),
            ft.Container(width=8), # Espaciador
            btn_portal
        ]
    )

    # ==================== 3. DISEÑO MÓVIL ====================
    def nav_item(texto: str, ruta: str, icono: ft.IconData):
        return ft.PopupMenuItem(
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Icon(icono, size=18, color=TEAL_DARK),
                    ft.Text(texto, size=14, color=TEXT_COLOR)
                ]
            ),
            on_click=lambda _: navegar(ruta)
        )

    menu_hamburguesa = ft.PopupMenuButton(
        icon=ft.Icons.MENU,
        icon_color=TEAL_DARK,
        tooltip="Menú Principal",
        items=[
            nav_item("Inicio", "/", ft.Icons.HOME_OUTLINED),
            nav_item("Quiénes Somos", "/quienes-somos", ft.Icons.INFO_OUTLINE),
            nav_item("Niveles", "/niveles", ft.Icons.ACCOUNT_TREE_OUTLINED),
            nav_item("Inscripción", "/inscripcion", ft.Icons.APP_REGISTRATION),
            nav_item("Contacto", "/contacto", ft.Icons.MAIL_OUTLINE),
        ]
    )

    derecha_movil = ft.Row(
        spacing=4,
        controls=[btn_portal, menu_hamburguesa]
    )

    # ==================== 4. LÓGICA RESPONSIVA ====================
    # Evaluamos el ancho de la pantalla al crear la barra
    es_celular = page.width < 768

    navbar_container = ft.Container(
        bgcolor=BG_WHITE,
        height=70,
        padding=ft.Padding.symmetric(horizontal=16 if es_celular else 32),
        border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                logo_area,
                derecha_movil if es_celular else derecha_desktop
            ]
        )
    )

    # Si el usuario achica o agranda la ventana en la PC, se actualiza en tiempo real
    def actualizar_navbar(e):
        ahora_es_celular = page.width < 768
        navbar_container.padding = ft.Padding.symmetric(horizontal=16 if ahora_es_celular else 32)
        navbar_container.content.controls[1] = derecha_movil if ahora_es_celular else derecha_desktop
        navbar_container.update()

    # Suscribimos el evento al redimensionar la pantalla
    page.on_resize = actualizar_navbar

    return navbar_container