import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

import flet.fastapi as flet_fastapi
from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.app import (
    models,  # noqa: F401  (registra todas las tablas en Base.metadata)
)
from backend.app.api.v1.api import api_router
from backend.app.core.database import Base, engine, get_db
from backend.app.core.scheduler import iniciar_scheduler
from backend.app.models.finanzas import ComprobantePago, Factura
from backend.app.models.personas import PadreAlumno
from backend.app.services.seguridad import seguridad_service
from frontend.app.main_view import main as flet_main
from mobile.main import main as mobile_main

# 1. Crear automáticamente las tablas en PostgreSQL si no existen
Base.metadata.create_all(bind=engine)


# 2. Definir el ciclo de vida de la aplicación (Encendido)
@asynccontextmanager
async def lifespan(app: FastAPI):
    iniciar_scheduler()  # Encendemos el motor de tareas automáticas
    yield  # La API queda corriendo...
    # (Acá iría código de apagado si hiciera falta)


# 2. Instancia principal de FastAPI
app = FastAPI(
    title="Educar para Transformar - API & Web",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 3. Middleware de CORS
#    - Local: localhost / 127.0.0.1
#    - Render: RENDER_EXTERNAL_URL se agrega automáticamente
#    - Otros orígenes: variable CORS_ORIGINS separada por comas
_origenes = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://educar-para-transformar-zcuo.onrender.com",
]

_render_url = os.getenv("RENDER_EXTERNAL_URL")
if _render_url:
    _origenes.append(_render_url.rstrip("/"))

_origenes += [
    origen.strip()
    for origen in os.getenv("CORS_ORIGINS", "").split(",")
    if origen.strip()
]

# Quitamos duplicados conservando el orden.
_origenes = list(dict.fromkeys(_origenes))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origenes,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. Endpoint de salud / prueba de la API
@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "message": "API REST funcionando correctamente"}


def _render_formulario_html(
    factura_id: int,
    token: str = "",
    error: str | None = None,
    exito: bool = False,
    archivo_nombre: str = "",
) -> HTMLResponse:
    display_form = "none" if exito else "block"
    display_success = "block" if exito else "none"
    display_error = "block" if error else "none"
    error_text = error or ""

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Subir Comprobante de Pago - Educar</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background: #f1f5f9; color: #1e293b; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 16px; }}
    .card {{ background: #ffffff; width: 100%; max-width: 420px; border-radius: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.08); padding: 24px; }}
    .header {{ text-align: center; margin-bottom: 20px; }}
    .icon-badge {{ width: 56px; height: 56px; border-radius: 28px; background: #e0f2f1; color: #0b4f4f; display: inline-flex; align-items: center; justify-content: center; font-size: 26px; margin-bottom: 10px; }}
    h1 {{ font-size: 19px; color: #0b4f4f; font-weight: 700; }}
    p.sub {{ font-size: 13px; color: #64748b; margin-top: 4px; }}
    .info-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
    .info-box span.label {{ font-size: 12px; color: #64748b; font-weight: 600; }}
    .info-box span.val {{ font-size: 14px; color: #0b4f4f; font-weight: 700; }}
    .dropzone {{ border: 2px dashed #0b4f4f; border-radius: 12px; background: #f0fdfa; padding: 24px 16px; text-align: center; cursor: pointer; transition: all 0.2s; }}
    .dropzone:active {{ background: #ccfbf1; }}
    .dropzone-icon {{ font-size: 36px; color: #0b4f4f; margin-bottom: 8px; }}
    .dropzone-text {{ font-size: 14px; font-weight: 600; color: #0b4f4f; }}
    .dropzone-subtext {{ font-size: 11px; color: #64748b; margin-top: 4px; }}
    .preview {{ display: none; background: #ecfdf5; border: 1px solid #10b981; border-radius: 10px; padding: 12px; margin-top: 14px; align-items: center; gap: 10px; }}
    .preview.active {{ display: flex; }}
    .preview-info {{ flex: 1; min-width: 0; }}
    .preview-name {{ font-size: 13px; font-weight: 600; color: #065f46; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .preview-size {{ font-size: 11px; color: #059669; }}
    .btn-submit {{ width: 100%; background: #0b4f4f; color: #ffffff; border: none; border-radius: 10px; padding: 14px; font-size: 14px; font-weight: 700; margin-top: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: background 0.2s; }}
    .btn-submit:disabled {{ background: #94a3b8; cursor: not-allowed; }}
    .success-box {{ text-align: center; padding: 20px 0; }}
    .success-icon {{ font-size: 52px; color: #10b981; margin-bottom: 12px; }}
    .error-msg {{ background: #fef2f2; border: 1px solid #f87171; color: #991b1b; padding: 10px; border-radius: 8px; font-size: 12px; margin-top: 12px; text-align: center; }}
    .spinner {{ display: none; width: 18px; height: 18px; border: 2px solid #ffffff; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  </style>
</head>
<body>
  <div class="card">
    <div id="form-container" style="display: {display_form};">
      <div class="header">
        <div class="icon-badge">📄</div>
        <h1>Comprobante de Pago</h1>
        <p class="sub">Educar para Transformar - Gestión Escolar</p>
      </div>

      <div class="info-box">
        <span class="label">Factura a abonar:</span>
        <span class="val">#{factura_id}</span>
      </div>

      <form id="upload_form" method="POST" action="/subir-comprobante" enctype="multipart/form-data" onsubmit="enviarFormulario()">
        <input type="hidden" name="factura_id" value="{factura_id}">
        <input type="hidden" name="token" value="{token}">
        <input type="file" name="archivo" id="input_file" accept=".pdf,application/pdf" style="display:none;" onchange="archivoSeleccionado(this)">

        <div class="dropzone" id="btn_pick" onclick="document.getElementById('input_file').click()">
          <div class="dropzone-icon">📁</div>
          <div class="dropzone-text">Tocar para seleccionar PDF</div>
          <div class="dropzone-subtext">Elegí el comprobante de tu celular (formato .PDF)</div>
        </div>

        <div class="preview" id="preview_box">
          <div style="font-size: 24px;">📑</div>
          <div class="preview-info">
            <div class="preview-name" id="preview_name">archivo.pdf</div>
            <div class="preview-size" id="preview_size">0 KB · Listo para enviar</div>
          </div>
        </div>

        <div class="error-msg" id="error_box" style="display: {display_error};">{error_text}</div>

        <button type="submit" class="btn-submit" id="btn_upload" disabled>
          <span class="spinner" id="spinner"></span>
          <span id="btn_text">Enviar Comprobante</span>
        </button>
      </form>
    </div>

    <div class="success-box" id="success_box" style="display: {display_success};">
      <div class="success-icon">✅</div>
      <h2 style="font-size: 18px; color: #065f46; margin-bottom: 8px;">¡Comprobante Enviado!</h2>
      <p style="font-size: 13px; color: #64748b; line-height: 1.5; margin-bottom: 12px;">
        Tu archivo <strong>{archivo_nombre}</strong> fue recibido exitosamente y se encuentra en revisión por el departamento de administración.
      </p>
      <p style="font-size: 12px; color: #0b4f4f; font-weight: 600; margin-bottom: 24px;">
        Podés cerrar esta ventana y regresar a la aplicación.
      </p>
      <button class="btn-submit" onclick="window.close()" style="background: #10b981;">
        Volver a la aplicación
      </button>
    </div>
  </div>

  <script>
    function archivoSeleccionado(input) {{
      const errorBox = document.getElementById('error_box');
      const previewBox = document.getElementById('preview_box');
      const previewName = document.getElementById('preview_name');
      const previewSize = document.getElementById('preview_size');
      const btnUpload = document.getElementById('btn_upload');

      errorBox.style.display = 'none';
      if (input.files && input.files[0]) {{
        const file = input.files[0];
        if (!file.name.toLowerCase().endsWith('.pdf')) {{
          errorBox.textContent = 'El archivo debe ser en formato .PDF';
          errorBox.style.display = 'block';
          btnUpload.disabled = true;
          previewBox.classList.remove('active');
          return;
        }}
        previewName.textContent = file.name;
        const kb = (file.size / 1024).toFixed(1);
        previewSize.textContent = kb + ' KB · Archivo válido';
        previewBox.classList.add('active');
        btnUpload.disabled = false;
      }}
    }}

    function enviarFormulario() {{
      const btnUpload = document.getElementById('btn_upload');
      const spinner = document.getElementById('spinner');
      const btnText = document.getElementById('btn_text');
      btnUpload.disabled = true;
      spinner.style.display = 'inline-block';
      btnText.textContent = 'Enviando archivo...';
    }}
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)


@app.get("/subir-comprobante", response_class=HTMLResponse)
def formulario_subir_comprobante(factura_id: int, token: str = ""):
    """Vista web responsiva para celulares y navegadores que permite seleccionar y subir un PDF real."""
    return _render_formulario_html(factura_id=factura_id, token=token)


@app.post("/subir-comprobante", response_class=HTMLResponse)
def procesar_subir_comprobante(
    factura_id: int = Form(...),
    token: str = Form(""),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Procesa el envío del comprobante PDF directamente mediante POST de formulario HTML sin depender de fetch."""
    try:
        if not token:
            return _render_formulario_html(
                factura_id=factura_id,
                token=token,
                error="Falta el token de autenticación. Inicie sesión nuevamente en la aplicación.",
            )

        user = seguridad_service.get_usuario_from_token(db, token)
        rol = seguridad_service.get_rol_nombre(db, user)
        if rol not in ("PARENT", "ADMIN"):
            return _render_formulario_html(
                factura_id=factura_id,
                token=token,
                error="No tiene permisos para subir comprobantes.",
            )

        factura = db.query(Factura).filter(Factura.id_factura == factura_id).first()
        if not factura:
            return _render_formulario_html(
                factura_id=factura_id,
                token=token,
                error="La factura indicada no existe.",
            )

        if user.id_padre:
            es_tutor = (
                db.query(PadreAlumno)
                .filter(
                    PadreAlumno.id_padre == user.id_padre,
                    PadreAlumno.legajo_alumno == factura.legajo_alumno,
                )
                .first()
            )
            if not es_tutor:
                return _render_formulario_html(
                    factura_id=factura_id,
                    token=token,
                    error="No tiene permiso para subir comprobantes de este alumno.",
                )

        nombre_original = archivo.filename or "comprobante.pdf"
        if not nombre_original.lower().endswith(".pdf"):
            return _render_formulario_html(
                factura_id=factura_id,
                token=token,
                error="Formato de archivo inválido. Solo se admiten archivos en formato .PDF.",
            )

        upload_dir = os.path.join(os.getcwd(), "uploads", "comprobantes")
        os.makedirs(upload_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sufijo_random = uuid.uuid4().hex[:6]
        nombre_seguro = f"fac_{factura_id}_{timestamp}_{sufijo_random}.pdf"
        ruta_destino = os.path.join(upload_dir, nombre_seguro)

        contenido = archivo.file.read()
        if len(contenido) == 0:
            return _render_formulario_html(
                factura_id=factura_id,
                token=token,
                error="El archivo PDF seleccionado está vacío.",
            )

        with open(ruta_destino, "wb") as f_out:
            f_out.write(contenido)

        url_relativa = f"/uploads/comprobantes/{nombre_seguro}"
        nuevo_comprobante = ComprobantePago(
            id_factura=factura_id,
            archivo_url=url_relativa,
            estado="PENDIENTE",
        )
        db.add(nuevo_comprobante)
        db.commit()

        return _render_formulario_html(
            factura_id=factura_id,
            token=token,
            exito=True,
            archivo_nombre=nombre_original,
        )

    except Exception as ex:
        return _render_formulario_html(
            factura_id=factura_id,
            token=token,
            error=f"Error al procesar el comprobante: {ex}",
        )


# Conectar routers REST
app.include_router(api_router, prefix="/api/v1")

# 5. Directorio estático para archivos adjuntos y comprobantes subidos
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(os.path.join(UPLOAD_DIR, "comprobantes"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 6. Montar la aplicación móvil dedicada en "/mobile"
app.mount(
    "/mobile",
    flet_fastapi.app(
        mobile_main,
        assets_dir=os.path.abspath(os.path.join(os.getcwd(), "mobile", "assets")),
    ),
)

# 7. Montar la interfaz de Flet Web en la raíz
# NOTA: Se monta AL FINAL para que las rutas de la API (/api/...) y la app móvil (/mobile) tengan prioridad
app.mount(
    "/",
    flet_fastapi.app(
        flet_main,
        assets_dir=os.path.abspath(
            os.path.join(os.getcwd(), "frontend", "app", "assets")
        ),
    ),
)
