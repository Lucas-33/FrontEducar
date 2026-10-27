import inspect

from frontend.app.main_view import main


def test_main_view_es_coroutine():
    """El entrypoint de la interfaz Flet debe ser asíncrono y estar exportado."""
    assert inspect.iscoroutinefunction(main)
