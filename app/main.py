from fastapi import FastAPI
import flet.fastapi as flet_fastapi

from app.api.routes import noticias
from app.ui.main_view import main as flet_main

app = FastAPI(title="Educar para Transformar")

app.include_router(noticias.router, prefix="/api/noticias", tags=["noticias"])

app.mount("/", flet_fastapi.app(flet_main))