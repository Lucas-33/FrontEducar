import flet as ft

COLOR_TEAL_DARK = "#0B4F4F"
COLOR_TEAL_MED = "#0D6E6E"
COLOR_TEAL_LIGHT = "#E6F2F2"
COLOR_BG = "#F5F7F7"
COLOR_CARD_BG = "#FFFFFF"
COLOR_BORDER = "#EAE6E1"
COLOR_TEXT_MAIN = "#1E2A29"
COLOR_TEXT_MUTED = "#5C6B69"
COLOR_SUCCESS = "#10B981"

def get_admin_reporte_transporte_pasajeros_view(page: ft.Page) -> ft.Control:
    data_pasajeros = [
        {"linea": "Línea Norte (Unidad 04)", "alumno": "Tomás Silva", "curso": "5° Grado A", "parada": "Av. San Martín 1420", "turno": "Ida / Vuelta", "tutor_contacto": "Laura Silva (3624-112233)"},
        {"linea": "Línea Norte (Unidad 04)", "alumno": "Lucía Morales", "curso": "3° Año A", "parada": "Plaza Central - Parada 2", "turno": "Solo Ida", "tutor_contacto": "Pedro Morales (3624-998877)"},
        {"linea": "Línea Norte (Unidad 04)", "alumno": "Esteban Quito", "curso": "Sala 4 Años", "parada": "Calle 8 y 21", "turno": "Ida / Vuelta", "tutor_contacto": "Marta Gómez (3624-445566)"},
        {"linea": "Línea Sur (Unidad 02)", "alumno": "Camila Beltrán", "curso": "2° Grado B", "parada": "Av. Castelli 800", "turno": "Ida / Vuelta", "tutor_contacto": "Andrés Beltrán (3624-332211)"},
        {"linea": "Línea Sur (Unidad 02)", "alumno": "Joaquín Ríos", "curso": "1° Año B", "parada": "Parque Urbano Sur", "turno": "Solo Vuelta", "tutor_contacto": "Silvia Ríos (3624-776655)"},
        {"linea": "Línea Oeste (Unidad 07)", "alumno": "Mía Cáceres", "curso": "6° Grado A", "parada": "B° San Cayetano Mz 4", "turno": "Ida / Vuelta", "tutor_contacto": "Hugo Cáceres (3624-665544)"},
    ]

    dd_linea = ft.Dropdown(
        label="Línea de Transporte",
        value="Todas",
        width=260,
        options=[
            ft.dropdown.Option("Todas"),
            ft.dropdown.Option("Línea Norte (Unidad 04)"),
            ft.dropdown.Option("Línea Sur (Unidad 02)"),
            ft.dropdown.Option("Línea Oeste (Unidad 07)"),
        ],
    )

    tf_filtro_parada = ft.TextField(
        label="Filtrar por Parada o Alumno",
        prefix_icon=ft.Icons.DIRECTIONS_BUS,
        expand=True,
    )

    txt_total_pasajeros = ft.Text("Total de Pasajeros: 0", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)

    table_data = ft.DataTable(
        border=ft.border.all(1, COLOR_BORDER),
        border_radius=8,
        heading_row_color=COLOR_TEAL_LIGHT,
        columns=[
            ft.DataColumn(ft.Text("Línea Asignada", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Alumno Pasajero", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Curso", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Parada / Dirección", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Modalidad", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
            ft.DataColumn(ft.Text("Tutor y Contacto Emergencia", weight=ft.FontWeight.BOLD, color=COLOR_TEAL_DARK)),
        ],
        rows=[],
    )

    def trigger_export(formato: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Exportando Hoja de Ruta de Pasajeros ({formato})..."),
            bgcolor=COLOR_TEAL_DARK,
        )
        page.snack_bar.open = True
        page.update()

    def update_table(e=None):
        linea_sel = dd_linea.value
        busqueda = tf_filtro_parada.value.strip().lower() if tf_filtro_parada.value else ""

        rows = []
        conteo = 0
        for p in data_pasajeros:
            match_linea = (linea_sel == "Todas") or (p["linea"] == linea_sel)
            match_busqueda = (busqueda in p["parada"].lower()) or (busqueda in p["alumno"].lower())

            if match_linea and match_busqueda:
                conteo += 1
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(p["linea"], weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(p["alumno"], weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN)),
                            ft.DataCell(ft.Text(p["curso"])),
                            ft.DataCell(ft.Text(p["parada"])),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(p["turno"], size=12, color=COLOR_TEAL_DARK, weight=ft.FontWeight.BOLD),
                                    bgcolor=COLOR_TEAL_LIGHT,
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                )
                            ),
                            ft.DataCell(ft.Text(p["tutor_contacto"])),
                        ]
                    )
                )
        table_data.rows = rows
        txt_total_pasajeros.value = f"Total de Pasajeros en Nómina: {conteo}"
        page.update()

    dd_linea.on_change = update_table
    tf_filtro_parada.on_change = update_table
    update_table()

    header_section = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(
                spacing=4,
                controls=[
                    ft.Text("Hoja de Ruta y Pasajeros de Transporte Escolar", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MAIN),
                    ft.Text("Planilla operativa para choferes, celadores y supervisión de recorridos.", size=14, color=COLOR_TEXT_MUTED),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.ElevatedButton(
                        "Planilla Chofer (PDF)",
                        icon=ft.Icons.PRINT,
                        style=ft.ButtonStyle(bgcolor=COLOR_TEAL_DARK, color=COLOR_CARD_BG),
                        on_click=lambda _: trigger_export("PDF"),
                    ),
                    ft.ElevatedButton(
                        "Excel Completo",
                        icon=ft.Icons.DOWNLOAD,
                        style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS, color=COLOR_CARD_BG),
                        on_click=lambda _: trigger_export("Excel"),
                    ),
                ],
            ),
        ],
    )

    return ft.Container(
        bgcolor=COLOR_BG,
        expand=True,
        padding=24,
        content=ft.Column(
            spacing=20,
            controls=[
                header_section,
                ft.Container(
                    bgcolor=COLOR_CARD_BG,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=10,
                    padding=16,
                    content=ft.Row(
                        spacing=16,
                        controls=[dd_linea, tf_filtro_parada],
                    ),
                ),
                ft.Row([txt_total_pasajeros], alignment=ft.MainAxisAlignment.END),
                ft.Container(
                    bgcolor=COLOR_CARD_BG,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=10,
                    padding=16,
                    content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[table_data]),
                ),
            ],
        ),
    )

if __name__ == "__main__":
    def main(page: ft.Page):
        page.title = "Educar SGE - Hoja de Ruta Transporte"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.add(get_admin_reporte_transporte_pasajeros_view(page))

    ft.run(main)
    