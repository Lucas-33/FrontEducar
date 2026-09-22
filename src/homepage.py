import flet as ft

#rama de marco

def main(page: ft.Page):
    # Configuración de página
    page.title = "Educar para Transformar - Quiénes Somos"
    page.bgcolor = "#FDFBF9" #[cite: 1]
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    # 1. Navbar
    navbar = ft.Container(
        bgcolor="#FFFFFF",
        border=ft.Border(bottom=ft.BorderSide(width=1, color="#EAE6E1")),
        padding=ft.Padding(left=80, top=0, right=80, bottom=0),
        height=90,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                # Logo y Título
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(width=40, height=40, bgcolor="#0D6E6E", border_radius=20), #[cite: 1]
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Educar para Transformar", size=18, weight=ft.FontWeight.BOLD, color="#0B4F4F"), #[cite: 1]
                                ft.Text("RESISTENCIA · K-12", size=11, color="#5C6B69") #[cite: 1]
                            ]
                        )
                    ]
                ),
                # Enlaces
                ft.Row(
                    spacing=32,
                    controls=[
                        ft.Text("Inicio", size=15, color="#1E2A29"), #[cite: 1]
                        ft.Text("Quiénes Somos", size=15, weight=ft.FontWeight.BOLD, color="#0D6E6E"), #[cite: 1]
                        ft.Text("Niveles", size=15, color="#1E2A29"), #[cite: 1]
                        ft.Text("Inscripción", size=15, color="#1E2A29"), #[cite: 1]
                        ft.Text("Noticias", size=15, color="#1E2A29"), #[cite: 1]
                    ]
                ),
                # Botón
                ft.Container(
                    bgcolor="#E6F2F2",
                    padding=ft.Padding(left=24, top=12, right=24, bottom=12),
                    border_radius=8,
                    content=ft.Text("PORTAL ACCESO", size=14, weight=ft.FontWeight.BOLD, color="#0B4F4F") #[cite: 1]
                )
            ]
        )
    )

    # 2. Sección Conocenos (Hero)
    hero = ft.Container(
        padding=ft.Padding(left=80, top=96, right=80, bottom=96),
        content=ft.Row(
            spacing=64,
            controls=[
                ft.Column(
                    width=666,
                    spacing=24,
                    controls=[
                        ft.Text("CONOCENOS", size=14, weight=ft.FontWeight.BOLD, color="#D97736"), #[cite: 1]
                        ft.Text("Nuestra Historia y Filosofía", size=36, weight=ft.FontWeight.BOLD, color="#0B4F4F"), #[cite: 1]
                        ft.Text("Fundado en la ciudad de Resistencia, Chaco, el Colegio Privado \"Educar para Transformar\" nació con el firme propósito de redefinir el paradigma educativo tradicional...", size=16, color="#5C6B69"), #[cite: 1]
                        ft.Text("Nuestra institución se destaca por su propuesta de jornada extendida, inmersión lingüística en múltiples idiomas...", size=16, color="#5C6B69") #[cite: 1]
                    ]
                ),
                # Placeholder para la imagen de arquitectura
                ft.Container(width=550, height=380, bgcolor="#EAE6E1", border_radius=16) 
            ]
        )
    )

    # 3. Misión y Visión
    mision_vision = ft.Container(
        bgcolor="#0B4F4F", #[cite: 1]
        padding=80,
        content=ft.Row(
            spacing=32,
            controls=[
                # Misión
                ft.Container(
                    bgcolor="#0D6E6E", #[cite: 1]
                    border_radius=16,
                    padding=40,
                    expand=True,
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Text("Nuestra Misión", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"), #[cite: 1]
                            ft.Text("Inspiramos, desafiamos y empoderamos a todos nuestros alumnos a ser miembros comprometidos y éticos...", size=16, color="#E6F2F2") #[cite: 1]
                        ]
                    )
                ),
                # Visión
                ft.Container(
                    bgcolor="#0D6E6E", #[cite: 1]
                    border_radius=16,
                    padding=40,
                    expand=True,
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Text("Nuestra Visión", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"), #[cite: 1]
                            ft.Text("Ser reconocidos como el centro educativo líder en el nordeste argentino por nuestra innovación pedagógica...", size=16, color="#E6F2F2") #[cite: 1]
                        ]
                    )
                )
            ]
        )
    )

    # Añadir todo a la página
    page.add(
        ft.Column(
            controls=[navbar, hero, mision_vision],
            spacing=0
        )
    )

ft.run(main)
