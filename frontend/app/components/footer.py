import flet as ft

GREEN = "#0B4F4F"
TEAL = "#117C7C"
TEAL_LIGHT = "#E6F2F2"
ORANGE = "#D97736"

def create_footer(page: ft.Page = None) -> ft.Container:
    """
    Genera el pie de página institucional responsivo.
    """
    return ft.Container(
        bgcolor=GREEN,
        padding=ft.Padding.symmetric(horizontal=60, vertical=64),
        content=ft.Column(
            spacing=48,
            controls=[
                ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        # Columna Institucional
                        ft.Container(
                            col={"sm": 12, "md": 5},
                            content=ft.Column(
                                spacing=16,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(ft.Icons.SCHOOL, color="white", size=22),
                                            ft.Text("Educar para Transformar", color="white", weight=ft.FontWeight.BOLD, size=20),
                                        ],
                                    ),
                                    ft.Text(
                                        "Inspiramos, desafiamos y empoderamos a todos nuestros alumnos a ser miembros comprometidos y éticos de una comunidad global.",
                                        color=TEAL_LIGHT,
                                        size=14,
                                    ),
                                ],
                            ),
                        ),
                        # Columna Niveles
                        ft.Container(
                            col={"sm": 6, "md": 2},
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text("NIVELES", color=ORANGE, weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text("Inicial (Jardín)", color="white", size=14),
                                    ft.Text("Primario", color="white", size=14),
                                    ft.Text("Secundario", color="white", size=14),
                                ],
                            ),
                        ),
                        # Columna Servicios
                        ft.Container(
                            col={"sm": 6, "md": 2},
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text("SERVICIOS", color=ORANGE, weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text("Comedor Escolar", color="white", size=14),
                                    ft.Text("Gabinete Psicopedagógico", color="white", size=14),
                                    ft.Text("Transporte Escolar", color="white", size=14),
                                ],
                            ),
                        ),
                        # Columna Contacto
                        ft.Container(
                            col={"sm": 12, "md": 3},
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text("CONTACTO", color=ORANGE, weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text("Av. Sarmiento 1200, Resistencia", color="white", size=14),
                                    ft.Text("+54 362 445-8900", color="white", size=14),
                                    ft.Text("administracion@educar.edu.ar", color="white", size=14),
                                ],
                            ),
                        ),
                    ],
                ),
                ft.Divider(color=TEAL, thickness=1),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    wrap=True,
                    controls=[
                        ft.Text("© 2024 Colegio Privado Educar para Transformar. Todos los derechos reservados.", color=TEAL_LIGHT, size=13),
                        ft.Text("Resistencia, Chaco, Argentina", color=TEAL_LIGHT, size=13),
                    ],
                ),
            ],
        ),
    )