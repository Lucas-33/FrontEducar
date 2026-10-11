# src/components/navbar.py
import flet as ft

GREEN = "#0B4F4F"
TEAL = "#117C7C"
TEAL_LIGHT = "#E6F2F2"
TEXT_COLOR = "#1E2A29"
MUTED = "#5C6B69"
BORDER_COLOR = "#EAE6E1"
BG_WHITE = "#FFFFFF"

def create_navbar(page: ft.Page, active_route: str = "/") -> ft.Container:
    def navegar(ruta: str):
        page.run_task(page.push_route, ruta)

    def nav_button(texto: str, ruta: str):
        es_activo = (active_route == ruta)
        return ft.Button(
            content=ft.Text(texto),
            bgcolor="transparent",
            color=TEAL if es_activo else TEXT_COLOR,
            elevation=0,
            style=ft.ButtonStyle(
                overlay_color="transparent",
                elevation=0,
                shadow_color="transparent",
            ),
            on_click=lambda _: navegar(ruta),
        )

    return ft.Container(
        bgcolor=BG_WHITE,
        height=90,
        padding=ft.Padding.symmetric(horizontal=40),
        border=ft.Border(bottom=ft.BorderSide(1, BORDER_COLOR)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.CLICK,
                    on_tap=lambda _: navegar("/"),
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=40,
                                height=40,
                                bgcolor=TEAL,
                                border_radius=20,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(ft.Icons.SCHOOL, color="white", size=22),
                            ),
                            ft.Column(
                                spacing=0,
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("Educar para Transformar", weight=ft.FontWeight.BOLD, size=18, color=GREEN),
                                    ft.Text("RESISTENCIA · K-12", size=11, color=MUTED),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Row(
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        nav_button("Inicio", "/"),
                        nav_button("Quiénes Somos", "/quienes-somos"),
                        nav_button("Niveles", "/niveles"),
                        nav_button("Inscripción", "/inscripcion"),
                        nav_button("Noticias", "/noticias"),
                        ft.Button(
                            "PORTAL ACCESO",
                            bgcolor=TEAL_LIGHT,
                            color=GREEN,
                            elevation=0,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=lambda _: navegar("/portal"),
                        ),
                    ],
                ),
            ],
        ),
    )