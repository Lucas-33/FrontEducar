import flet as ft

# Paleta y constantes de diseño
BG_PAGE = "#FDFBF9"
BG_WHITE = "#FFFFFF"
TEAL_DARK = "#0B4F4F"
TEAL = "#0D6E6E"
TEAL_LIGHT = "#E6F2F2"
ORANGE = "#D97736"
MUTED = "#5C6B69"


def get_niveles_view(page: ft.Page) -> list[ft.Control]:
    """Retorna los bloques de contenido central para la página de Niveles Educativos."""

    # ==================== HELPERS DE SECCIÓN ====================
    def header_seccion(tag: str, titulo: str) -> ft.Column:
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Text(
                    tag.upper(),
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=ORANGE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    titulo,
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    color=TEAL_DARK,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        )

    def badge_caracteristica(icono_emoji: str, texto: str, color_texto: str) -> ft.Row:
        return ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(icono_emoji, size=16),
                ft.Text(texto, size=14, weight=ft.FontWeight.W_600, color=color_texto),
            ],
        )

    def bloque_nivel(
        titulo: str,
        descripcion: str,
        jornada: str,
        idiomas: str,
        imagen_url: str,
        imagen_a_la_derecha: bool = False,
    ) -> ft.ResponsiveRow:
        col_info = ft.Container(
            col={"sm": 12, "md": 7},
            content=ft.Column(
                spacing=24,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(titulo, size=32, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                    ft.Text(
                        descripcion,
                        size=16,
                        color=MUTED,
                        height=1.5,
                    ),
                    ft.Column(
                        spacing=12,
                        controls=[
                            badge_caracteristica("🕒", jornada, ORANGE),
                            badge_caracteristica("🌐", idiomas, TEAL),
                        ],
                    ),
                ],
            ),
        )

        col_imagen = ft.Container(
            col={"sm": 12, "md": 5},
            border_radius=16,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Image(
                src=imagen_url,
                fit="cover",
                height=350,
            ),
        )

        controles = [col_info, col_imagen] if imagen_a_la_derecha else [col_imagen, col_info]

        return ft.ResponsiveRow(
            columns=12,
            spacing=64,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controles,
        )

    # ==================== SECCIÓN 1: PROPUESTA ACADÉMICA ====================
    propuesta_academica = ft.Container(
        bgcolor=BG_PAGE,
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.Column(
            spacing=64,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                header_seccion("Niveles", "Nuestra Propuesta Académica"),
                # Nivel Inicial (Imagen Izquierda, Texto Derecha)
                bloque_nivel(
                    titulo="Nivel Inicial",
                    descripcion=(
                        "Nuestros espacios para el jardín de infantes están diseñados para "
                        "fomentar la curiosidad natural del niño en un ambiente lúdico y estimulante."
                    ),
                    jornada="Jornada Extendida (08:00 a 16:00 hs)",
                    idiomas="Iniciación al Inglés y Portugués",
                    imagen_url="https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&h=420&fit=crop",
                    imagen_a_la_derecha=False,
                ),
                # Nivel Primario (Texto Izquierda, Imagen Derecha)
                bloque_nivel(
                    titulo="Nivel Primario",
                    descripcion=(
                        "Consolidamos las bases de un pensamiento crítico y colaborativo, "
                        "impulsando la curiosidad intelectual de manera estructurada."
                    ),
                    jornada="Doble Escolaridad Obligatoria (07:30 a 16:30 hs)",
                    idiomas="Inglés Intensivo, Introducción al Francés y Portugués",
                    imagen_url="https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600&h=420&fit=crop",
                    imagen_a_la_derecha=True,
                ),
                # Nivel Secundario (Imagen Izquierda, Texto Derecha)
                bloque_nivel(
                    titulo="Nivel Secundario",
                    descripcion=(
                        "Preparamos a nuestros estudiantes para los desafíos universitarios y laborales, "
                        "impulsando el liderazgo, el espíritu emprendedor y la conciencia ética global."
                    ),
                    jornada="Doble Turno y Actividades Deportivas (07:30 a 17:30 hs)",
                    idiomas="Trilingüe con certificaciones internacionales",
                    imagen_url="https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=600&h=420&fit=crop",
                    imagen_a_la_derecha=False,
                ),
            ],
        ),
    )

    # ==================== SECCIÓN 2: SERVICIOS DE APOYO ====================
    def tarjeta_servicio(icono: ft.IconData, titulo: str, descripcion: str) -> ft.Container:
        return ft.Container(
            col={"sm": 12, "md": 4},
            bgcolor=BG_WHITE,
            border_radius=16,
            padding=32,
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        bgcolor=TEAL_LIGHT,
                        border_radius=24,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, color=TEAL, size=24),
                    ),
                    ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                    ft.Text(
                        descripcion,
                        size=14,
                        color=MUTED,
                        height=1.5,
                    ),
                ],
            ),
        )

    servicios_apoyo = ft.Container(
        bgcolor=TEAL_LIGHT,
        padding=ft.Padding.symmetric(horizontal=80, vertical=96),
        content=ft.Column(
            spacing=56,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                header_seccion("Comunidad Cuidada", "Servicios de Apoyo al Alumno"),
                ft.ResponsiveRow(
                    columns=12,
                    spacing=32,
                    controls=[
                        tarjeta_servicio(
                            icono=ft.Icons.FAVORITE_BORDER,
                            titulo="Servicio de Enfermería",
                            descripcion="Atención de primeros auxilios constante a cargo de enfermeros matriculados.",
                        ),
                        tarjeta_servicio(
                            icono=ft.Icons.PEOPLE_OUTLINE,
                            titulo="Gabinete Psicopedagógico",
                            descripcion="Acompañamiento en el desarrollo socio-emocional y de aprendizaje.",
                        ),
                        tarjeta_servicio(
                            icono=ft.Icons.DIRECTIONS_BUS_OUTLINED,
                            titulo="Transporte Escolar",
                            descripcion="Flota propia de micros con choferes calificados y seguimiento por GPS.",
                        ),
                    ],
                ),
            ],
        ),
    )

    return [propuesta_academica, servicios_apoyo]