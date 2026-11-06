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
    ONLINE_GREEN,
    TEAL,
    TEAL_DARK,
    TEXT_COLOR,
)

async def get_admin_finanzas_view(page: ft.Page) -> ft.Row:
    """Pantalla para que el Administrador configure los precios del sistema."""

    token_almacenado = getattr(page, "auth_token", None)
    if token_almacenado and api_client.token != token_almacenado:
        api_client.set_token(token_almacenado)

    aviso = ft.Text("", size=13, weight=ft.FontWeight.W_600, visible=False)

    def mostrar_mensaje(texto: str, es_error: bool = False):
        aviso.value = texto
        aviso.color = BADGE_RED_TXT if es_error else ONLINE_GREEN
        aviso.visible = True
        page.update()

    def campo_precio(label: str, valor_inicial: str = "0.00") -> ft.TextField:
        return ft.TextField(
            label=label,
            value=valor_inicial,
            prefix=ft.Text("$ ", color=TEXT_COLOR),
            text_size=14,
            color=TEXT_COLOR, # <--- FUENTE NEGRA / OSCURA DENTRO DEL INPUT
            width=280,
            height=CONTROL_HEIGHT,
            border_color=BORDER_COLOR,
            focused_border_color=TEAL,
            border_radius=BORDER_RADIUS,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$"),
        )

    # ==================== 1. VALORES INSTITUCIONALES FIJOS ====================
    input_cuota = campo_precio("Valor de la Cuota Base Mensual")
    input_comedor = campo_precio("Valor Mensual del Comedor")

    async def guardar_fijos(e):
        try:
            val_cuota = float(input_cuota.value or 0)
            val_comedor = float(input_comedor.value or 0)
            await api_client.update_configuracion("CUOTA_BASE", val_cuota)
            await api_client.update_configuracion("COMEDOR", val_comedor)
            mostrar_mensaje("Valores institucionales actualizados correctamente.")
        except Exception as err:
            mostrar_mensaje(f"Error al guardar: {err}", es_error=True)

    card_fijos = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Cuota Base y Comedor", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                ft.Text("Estos valores impactarán en la facturación del próximo mes para todos los inscriptos.", size=13, color=MUTED),
                ft.Row(spacing=16, controls=[input_cuota, input_comedor]),
                ft.Button(
                    "Guardar Valores Fijos",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=guardar_fijos,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                )
            ]
        )
    )

    # ==================== 2. VALORES DE DEPORTES ====================
    lista_deportes = ft.Column(spacing=12)

    async def cargar_datos():
        # --- 1. Cargar Precios Fijos ---
        try:
            cuota_data = await api_client.get_configuracion("CUOTA_BASE")
            comedor_data = await api_client.get_configuracion("COMEDOR")
            
            input_cuota.value = str(cuota_data.get("valor", "0.00"))
            input_comedor.value = str(comedor_data.get("valor", "0.00"))
        except Exception:
            pass 

        # --- 2. Cargar Deportes ---
        try:
            deportes = await api_client.get_deportes()
            filas = []
            inputs_deportes = [] # Guardamos las referencias para procesarlas todas juntas
            
            for d in deportes:
                input_precio = campo_precio(f"Precio: {d['nombre']}", str(d.get("precio_mensual", 0)))
                inputs_deportes.append({"id_deporte": d["id_deporte"], "nombre": d["nombre"], "input": input_precio})
                
                filas.append(ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(d["nombre"], size=14, weight=ft.FontWeight.W_600, color=TEXT_COLOR, width=200),
                        input_precio,
                        # Eliminamos el botón individual de cada fila
                    ]
                ))

            if filas:
                # Botón global para guardar todos los deportes a la vez
                async def guardar_todos_deportes(e):
                    errores = 0
                    for item in inputs_deportes:
                        try:
                            await api_client.update_deporte(
                                item["id_deporte"], 
                                {"nombre": item["nombre"], "precio_mensual": float(item["input"].value or 0)}
                            )
                        except Exception:
                            errores += 1
                    
                    if errores == 0:
                        mostrar_mensaje("Todos los precios deportivos se actualizaron correctamente.")
                    else:
                        mostrar_mensaje(f"Se guardó parcialmente: hubo {errores} errores.", es_error=True)

                btn_guardar_deportes = ft.Button(
                    "Guardar Precios Deportivos",
                    bgcolor=TEAL,
                    color=BG_WHITE,
                    on_click=guardar_todos_deportes,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS)),
                )
                
                filas.append(ft.Container(height=8)) # Un pequeño espacio
                filas.append(btn_guardar_deportes) # Agregamos el botón al final de la lista

            lista_deportes.controls = filas or [ft.Text("No hay deportes registrados.", color=MUTED)]
        except Exception:
            lista_deportes.controls = [ft.Text("Error al cargar deportes.", color=BADGE_RED_TXT)]

        # --- 3. Refrescar UI ---
        page.update()

    # Ejecutar al entrar a la pantalla
    page.run_task(cargar_datos)

    card_deportes = ft.Container(
        bgcolor=BG_WHITE,
        border=ft.Border.all(1, BORDER_COLOR),
        border_radius=CARD_RADIUS,
        padding=24,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Precios de Disciplinas Deportivas", size=18, weight=ft.FontWeight.BOLD, color=TEAL_DARK),
                lista_deportes
            ]
        )
    )

    return admin_layout(
        page=page,
        titulo="Gestión de Precios y Finanzas",
        active_route="/admin/finanzas",
        content_controls=[
            aviso,
            ft.Row(
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(expand=True, spacing=24, controls=[card_fijos]),
                    ft.Column(expand=True, spacing=24, controls=[card_deportes]),
                ]
            )
        ],
    )