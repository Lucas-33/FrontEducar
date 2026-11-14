import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "tu_correo@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "tu_clave_de_aplicacion_gmail")


def enviar_correo_con_pdf(
    destinatario: str | list[str],
    asunto: str,
    cuerpo: str,
    ruta_pdf: str | None = None,
    borrar_despues: bool = False,
) -> bool:
    """Envía un correo electrónico con un archivo adjunto PDF a uno o más destinatarios.

    Si las credenciales SMTP no están configuradas o fallan en entorno de desarrollo,
    registra el envío simulado para facilitar pruebas y desarrollo local.
    """
    if not destinatario:
        return False

    lista_destinatarios = (
        [destinatario]
        if isinstance(destinatario, str)
        else [d for d in destinatario if d]
    )
    if not lista_destinatarios:
        return False

    pdf_data: bytes | None = None
    pdf_name: str | None = None

    if ruta_pdf and os.path.exists(ruta_pdf):
        try:
            with open(ruta_pdf, "rb") as f:
                pdf_data = f.read()
                pdf_name = os.path.basename(ruta_pdf)
        except Exception as e:
            print(f"⚠️ Error leyendo archivo PDF {ruta_pdf}: {e}")

    # Verificar si estamos en modo simulación (sin credenciales SMTP reales)
    es_simulado = (
        not EMAIL_SENDER
        or not EMAIL_PASSWORD
        or EMAIL_SENDER in ("tu_correo@gmail.com", "admin@educar.local")
        or EMAIL_PASSWORD == "tu_clave_de_aplicacion_gmail"
    )

    exito_total = True
    for dest in lista_destinatarios:
        if es_simulado:
            print(
                f"📧 [SIMULACIÓN CORREO] Para: {dest} | Asunto: '{asunto}' | Adjunto: {pdf_name or 'Sin adjunto'}"
            )
            continue

        msg = EmailMessage()
        msg["Subject"] = asunto
        msg["From"] = EMAIL_SENDER
        msg["To"] = dest
        msg.set_content(cuerpo)

        if pdf_data and pdf_name:
            msg.add_attachment(
                pdf_data, maintype="application", subtype="pdf", filename=pdf_name
            )

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"📧 Correo enviado exitosamente a {dest}")
        except Exception as e:
            print(f"❌ Error enviando correo a {dest} vía SMTP: {e}")
            print(f"ℹ️ [FALLBACK LOCAL] Contenido para {dest}:\n{cuerpo}")
            exito_total = False

    if borrar_despues and ruta_pdf and os.path.exists(ruta_pdf):
        try:
            os.remove(ruta_pdf)
        except Exception:
            pass

    return exito_total
