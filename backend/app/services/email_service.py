import os
import smtplib
from email.message import EmailMessage
from typing import Any

from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "tu_correo@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "tu_clave_de_aplicacion_gmail")


def obtener_config_smtp() -> tuple[str, int, str, str]:
    """Obtiene la configuración SMTP actual desde el entorno o archivo .env."""
    load_dotenv()
    servidor = os.getenv("SMTP_SERVER", "smtp.gmail.com").strip()
    puerto = int(os.getenv("SMTP_PORT", "587"))
    remitente = os.getenv("EMAIL_SENDER", "").strip()
    # Limpiamos posibles espacios que Google muestra en los bloques de 4 letras
    clave = os.getenv("EMAIL_PASSWORD", "").strip().replace(" ", "")
    return servidor, puerto, remitente, clave


def es_modo_simulado(remitente: str, clave: str) -> bool:
    """Determina si el sistema debe operar en modo simulación (consola) o SMTP real."""
    return (
        not remitente
        or not clave
        or remitente in ("tu_correo@gmail.com", "admin@educar.local")
        or clave == "tu_clave_de_aplicacion_gmail"
    )


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

    servidor, puerto, remitente, clave = obtener_config_smtp()
    simulado = es_modo_simulado(remitente, clave)

    exito_total = True
    for dest in lista_destinatarios:
        if simulado:
            print(
                f"📧 [SIMULACIÓN CORREO] Para: {dest} | Asunto: '{asunto}' | Adjunto: {pdf_name or 'Sin adjunto'}"
            )
            continue

        msg = EmailMessage()
        msg["Subject"] = asunto
        msg["From"] = remitente
        msg["To"] = dest
        msg.set_content(cuerpo)

        if pdf_data and pdf_name:
            msg.add_attachment(
                pdf_data,
                maintype="application",
                subtype="pdf",
                filename=pdf_name,
            )

        try:
            if puerto == 465:
                with smtplib.SMTP_SSL(servidor, puerto, timeout=12) as server:
                    server.login(remitente, clave)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(servidor, puerto, timeout=12) as server:
                    server.starttls()
                    server.login(remitente, clave)
                    server.send_message(msg)
            print(f"📧 Correo enviado exitosamente a {dest}")
        except smtplib.SMTPAuthenticationError as auth_err:
            print(f"❌ Error de autenticación SMTP con {servidor}: {auth_err}")
            print(
                "💡 Recordatorio para Gmail: Debes usar una 'Contraseña de aplicación' de 16 caracteres "
                "(Gestionar cuenta de Google > Seguridad > Verificación en dos pasos > Contraseñas de aplicaciones)."
            )
            exito_total = False
        except smtplib.SMTPServerDisconnected as disc_err:
            print(f"❌ Google cerró la conexión al validar credenciales: {disc_err}")
            print(
                f"💡 La clave configurada tiene {len(clave)} caracteres. "
                "Las contraseñas de aplicación de Google siempre tienen exactamente 16 letras minúsculas (ej: abcd efgh ijkl mnop). "
                "Verificá en myaccount.google.com/apppasswords que no falten caracteres."
            )
            exito_total = False
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


def probar_conexion_email(
    destinatario: str, ruta_pdf: str | None = None
) -> dict[str, Any]:
    """Prueba la conexión directa con el servidor SMTP y envía un correo de diagnóstico."""
    servidor, puerto, remitente, clave = obtener_config_smtp()

    if es_modo_simulado(remitente, clave):
        return {
            "exito": True,
            "modo": "SIMULADO",
            "mensaje": (
                "El sistema está en modo simulación porque no se configuraron EMAIL_SENDER ni "
                "EMAIL_PASSWORD en el archivo .env. Los correos se registrarán en la consola del servidor."
            ),
            "destinatario": destinatario,
            "remitente_configurado": remitente or "No configurado",
            "servidor": f"{servidor}:{puerto}",
        }

    asunto = "Prueba de Integración SMTP - Educar para Transformar"
    cuerpo = (
        "¡Hola!\n\n"
        "Este es un correo de prueba enviado desde el Sistema de Gestión Escolar 'Educar para Transformar'.\n\n"
        "La integración con el servidor de correo SMTP (Gmail) está funcionando correctamente.\n"
        f"• Servidor: {servidor}:{puerto}\n"
        f"• Remitente: {remitente}\n"
        f"• Destinatario: {destinatario}\n\n"
        "Saludos cordiales,\n"
        "Equipo de Administración y Soporte"
    )

    pdf_data: bytes | None = None
    pdf_name: str | None = None
    if ruta_pdf and os.path.exists(ruta_pdf):
        try:
            with open(ruta_pdf, "rb") as f:
                pdf_data = f.read()
                pdf_name = os.path.basename(ruta_pdf)
        except Exception:
            pass

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario
    msg.set_content(cuerpo)
    if pdf_data and pdf_name:
        msg.add_attachment(
            pdf_data, maintype="application", subtype="pdf", filename=pdf_name
        )

    try:
        if puerto == 465:
            with smtplib.SMTP_SSL(servidor, puerto, timeout=12) as server:
                server.login(remitente, clave)
                server.send_message(msg)
        else:
            with smtplib.SMTP(servidor, puerto, timeout=12) as server:
                server.starttls()
                server.login(remitente, clave)
                server.send_message(msg)

        return {
            "exito": True,
            "modo": "REAL",
            "mensaje": f"Correo de prueba enviado exitosamente a {destinatario} vía {servidor}.",
            "destinatario": destinatario,
            "remitente": remitente,
            "servidor": f"{servidor}:{puerto}",
            "adjunto": pdf_name or "Sin adjunto",
        }
    except (
        smtplib.SMTPAuthenticationError,
        smtplib.SMTPServerDisconnected,
    ) as auth_err:
        longitud_actual = len(clave)
        return {
            "exito": False,
            "modo": "ERROR_AUTENTICACION_GMAIL",
            "mensaje": (
                "Google rechazó las credenciales (Error 535 BadCredentials). "
                f"Tu contraseña configurada tiene {longitud_actual} caracteres, pero las 'Contraseñas de aplicación' de Google tienen exactamente 16 letras (4 grupos de 4: abcd efgh ijkl mnop). "
                "Verificá que no te hayan faltado caracteres al copiarla desde myaccount.google.com/apppasswords."
            ),
            "detalle": f"{type(auth_err).__name__}: {auth_err}",
            "longitud_clave_configurada": longitud_actual,
            "servidor": f"{servidor}:{puerto}",
            "remitente": remitente,
        }
    except Exception as ex:
        return {
            "exito": False,
            "modo": "ERROR_CONEXION",
            "mensaje": f"No se pudo conectar al servidor SMTP: {ex}",
            "detalle": str(ex),
            "servidor": f"{servidor}:{puerto}",
            "remitente": remitente,
        }
