"""Paquete de la interfaz Flet de Educar para Transformar.

El paquete es importable con dos nombres según el contexto de ejecución:

- ``frontend.app`` — cuando se ejecuta desde la raíz del proyecto
  (por ejemplo ``python frontend/run.py`` o el deploy de Render, donde la
  raíz del repositorio está en ``sys.path``).
- ``app`` — cuando ``frontend/`` es la raíz de la aplicación, que es lo que
  ocurre dentro de un paquete generado con ``flet build`` (APK, AAB, etc.):
  el bundler copia el contenido de ``frontend/`` y el entry point
  ``main.py`` importa ``from app.main_view import main``.

El alias de ``sys.modules`` que sigue registra el nombre corto cuando el
paquete se carga con el nombre largo, de modo que los imports internos
``from app.<modulo> import ...`` funcionan en ambos contextos.
"""

import sys

if __name__ == "frontend.app":
    sys.modules.setdefault("app", sys.modules[__name__])
