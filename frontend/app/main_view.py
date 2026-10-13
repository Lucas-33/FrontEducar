import importlib
import inspect
import flet as ft

def cargar_controlador(modulo: str, *candidatos):
    try:
        mod = importlib.import_module(f"frontend.app.pages.{modulo}")
        for c in candidatos:
            if hasattr(mod, c):
                return getattr(mod, c)
        for attr in dir(mod):
            if attr.endswith("_view") and callable(getattr(mod, attr)):
                return getattr(mod, attr)
    except Exception as err:
        print(f"[main_view] Error importando '{modulo}': {err}")
    return None

v_home = cargar_controlador("home", "home_view", "get_home_view")
v_niveles = cargar_controlador("niveles", "niveles_view", "get_niveles_view")
v_bienestar = cargar_controlador("bienestar", "bienestar_view", "get_bienestar_view")
v_inscripciones = cargar_controlador("inscripciones", "inscripciones_view", "get_inscripciones_view")
v_noticias = cargar_controlador("noticias", "noticias_view", "get_noticias_view")
v_opiniones = cargar_controlador("opiniones", "opiniones_view", "get_opiniones_view")
v_empleo = cargar_controlador("empleo", "empleo_view", "get_empleo_view")
v_contacto = cargar_controlador("contacto", "contacto_view", "get_contacto_view")
v_login = cargar_controlador("login", "get_login_view", "login_view")

v_admin_dash = cargar_controlador("admin_dashboard", "admin_dashboard_view", "get_admin_dashboard_view")
v_admin_alumnos = cargar_controlador("admin_alumnos", "get_admin_alumnos_view", "admin_alumnos_view")
v_admin_alumno_form = cargar_controlador("admin_alumno_form", "get_admin_alumno_form_view", "admin_alumno_form_view")
v_admin_profesores = cargar_controlador("admin_profesores", "admin_profesores_view", "get_admin_profesores_view")
v_admin_cursos = cargar_controlador("admin_cursos", "admin_cursos_view", "get_admin_cursos_view")
v_admin_deportes = cargar_controlador("admin_deportes", "admin_deportes_view", "get_admin_deportes_view")

v_portal_docente = cargar_controlador("portal_docente", "portal_docente_view", "get_portal_docente_view")
v_portal_padre = cargar_controlador("portal_padre", "portal_padre_view", "get_portal_padre_view")
v_portal_alumno = cargar_controlador("portal_alumno", "portal_alumno_view", "get_portal_alumno_view")


async def main(page: ft.Page):
    page.title = "Educar para Transformar"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0

    async def resolver_controles(generador):
        if generador is None:
            return [ft.Container(padding=40, content=ft.Text("Módulo en construcción", size=18))]
        if inspect.iscoroutinefunction(generador):
            res = await generador(page)
        else:
            res = generador(page)
        return res if isinstance(res, list) else [res]

    # EVENTO NATIVO DE FLET (sin hacks asíncronos que rompan los clics)
    async def route_change(e):
        page.views.clear()
        ruta = (page.route or "/").rstrip("/")
        if not ruta:
            ruta = "/"

        if ruta == "/":
            controles = await resolver_controles(v_home)
        elif ruta == "/niveles":
            controles = await resolver_controles(v_niveles)
        elif ruta == "/bienestar":
            controles = await resolver_controles(v_bienestar)
        elif ruta in ("/inscripciones", "/admisiones"):
            controles = await resolver_controles(v_inscripciones)
        elif ruta == "/noticias":
            controles = await resolver_controles(v_noticias)
        elif ruta == "/opiniones":
            controles = await resolver_controles(v_opiniones)
        elif ruta == "/empleo":
            controles = await resolver_controles(v_empleo)
        elif ruta == "/contacto":
            controles = await resolver_controles(v_contacto)
        elif ruta in ("/login", "/portal"):
            controles = await resolver_controles(v_login)
        elif ruta == "/admin/dashboard":
            controles = await resolver_controles(v_admin_dash)
        elif ruta == "/admin/alumnos":
            controles = await resolver_controles(v_admin_alumnos)
        elif ruta in ("/admin/alumnos/nuevo", "/admin/alumnos/editar"):
            controles = await resolver_controles(v_admin_alumno_form)
        elif ruta == "/admin/profesores":
            controles = await resolver_controles(v_admin_profesores)
        elif ruta == "/admin/cursos":
            controles = await resolver_controles(v_admin_cursos)
        elif ruta == "/admin/deportes":
            controles = await resolver_controles(v_admin_deportes)
        elif ruta == "/portal/docente/dashboard":
            controles = await resolver_controles(v_portal_docente)
        elif ruta == "/portal/padre/dashboard":
            controles = await resolver_controles(v_portal_padre)
        elif ruta == "/portal/alumno/dashboard":
            controles = await resolver_controles(v_portal_alumno)
        else:
            controles = [
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=60,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16,
                        controls=[
                            ft.Text("404 — Página no encontrada", size=24, weight=ft.FontWeight.BOLD),
                            ft.Button("Volver al Inicio", on_click=lambda _: page.go("/")),
                        ],
                    ),
                )
            ]

        page.views.append(ft.View(route=ruta, padding=0, controls=controles))
        page.update()

    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await route_change(None)