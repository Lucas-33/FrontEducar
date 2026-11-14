import os
import smtplib
from email.message import EmailMessage

# ⚠️ NOTA: Usar variables de entorno en producción. Acá podés hardcodear tu correo para probar.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "tu_correo@gmail.com") 
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "tu_clave_de_aplicacion_gmail") 

def enviar_correo_con_pdf(destinatario: str, asunto: str, cuerpo: str, ruta_pdf: str = None):
    """Envía un correo electrónico con un archivo adjunto PDF (y luego borra el PDF temporal)."""
    if not destinatario:
        return

    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = EMAIL_SENDER
    msg['To'] = destinatario
    msg.set_content(cuerpo)

    # Adjuntar PDF si existe
    if ruta_pdf and os.path.exists(ruta_pdf):
        with open(ruta_pdf, 'rb') as f:
            pdf_data = f.read()
            pdf_name = os.path.basename(ruta_pdf)
        
        msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=pdf_name)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"📧 Correo enviado exitosamente a {destinatario}")
    except Exception as e:
        print(f"❌ Error enviando correo a {destinatario}: {e}")
    finally:
        # Limpiar el PDF temporal de tu disco duro
        if ruta_pdf and os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)