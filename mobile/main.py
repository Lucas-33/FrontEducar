"""Entrada principal para la Aplicación Móvil de Educar para Transformar.

Ejecución local para emulador o celular con Flet (desde la raíz del proyecto):

    uv run flet run mobile/main.py
"""

import sys
from pathlib import Path

# Permite resolver imports de mobile.* independientemente de cómo se invoque el script
raiz_proyecto = Path(__file__).resolve().parent.parent
if str(raiz_proyecto) not in sys.path:
    sys.path.insert(0, str(raiz_proyecto))

import flet as ft

from mobile.api_client import mobile_api
from mobile.components.constants import BG_PAGE, TEAL
from mobile.components.mobile_scaffold import create_mobile_scaffold
from mobile.pages.facturas_page import get_facturas_page
from mobile.pages.home_page import get_home_page
from mobile.pages.login_page import get_login_page
from mobile.pages.perfil_page import get_perfil_page
from mobile.pages.servicios_page import get_servicios_page


async def main(page: ft.Page):
    page.title = "Educar Móvil"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.theme = ft.Theme(
        color_scheme_seed=TEAL,
        font_family="Roboto",
    )

    tab_actual = 0

    def cerrar_sesion():
        page.auth_token = None
        page.auth_rol = None
        page.auth_user = None
        page.auth_padre_id = None
        mobile_api.clear_token()
        mostrar_login()

    def cambiar_tab(nuevo_indice: int):
        nonlocal tab_actual
        tab_actual = nuevo_indice
        renderizar_pantalla_actual()

    def renderizar_pantalla_actual():
        page.views.clear()

        # Selección de título y contenido según el tab activo
        if tab_actual == 0:
            titulo = "Inicio"
            contenido = get_home_page(page, on_navegar_tab=cambiar_tab)
        elif tab_actual == 1:
            titulo = "Mis Cuotas"
            contenido = get_facturas_page(page)
        elif tab_actual == 2:
            titulo = "Servicios"
            contenido = get_servicios_page(page)
        else:
            titulo = "Mi Perfil"
            contenido = get_perfil_page(page, on_cerrar_sesion=cerrar_sesion)

        scaffold = create_mobile_scaffold(
            page=page,
            titulo=titulo,
            contenido=contenido,
            indice_activo=tab_actual,
            on_cambiar_tab=cambiar_tab,
            on_refresh=renderizar_pantalla_actual,
        )

        page.views.append(
            ft.View(
                route="/app",
                padding=0,
                bgcolor=BG_PAGE,
                controls=[scaffold],
            )
        )
        page.update()

    def mostrar_login():
        page.views.clear()
        login_view = get_login_page(page, on_login_success=mostrar_app)
        page.views.append(
            ft.View(
                route="/login",
                padding=0,
                bgcolor=BG_PAGE,
                controls=[login_view],
            )
        )
        page.update()

    def mostrar_app():
        nonlocal tab_actual
        tab_actual = 0
        renderizar_pantalla_actual()

    # Si hay sesión iniciada va al app, sino al login
    token_existente = getattr(page, "auth_token", None)
    if token_existente:
        mostrar_app()
    else:
        mostrar_login()


if __name__ == "__main__":
    ft.run(main)
