import flet.fastapi as flet_fastapi
from fastapi import FastAPI

from app.ui.main_view import main as flet_main

app = FastAPI(title="Educar para Transformar")

app.mount("/", flet_fastapi.app(flet_main))
