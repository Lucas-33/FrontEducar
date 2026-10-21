import os

# Carpetas a ignorar para no copiar basura
IGNORAR_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'alembic'}
# Extensiones de código que queremos leer
EXTENSIONES = {'.py', '.pgsql', '.sql', '.md', '.txt'}

archivo_salida = "proyecto_completo.txt"

with open(archivo_salida, "w", encoding="utf-8") as outfile:
    # os.walk recorre desde la carpeta donde ejecutás el script hacia adentro
    for root, dirs, files in os.walk("."):
        # Modificamos la lista de carpetas para que no entre en las ignoradas
        dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONES) and file != "unificar.py":
                filepath = os.path.join(root, file)
                
                # Separador visual y nombre del archivo
                outfile.write(f"\n{'='*60}\n")
                outfile.write(f"--- RUTA: {filepath} ---\n")
                outfile.write(f"{'='*60}\n\n")
                
                # Leer el contenido y pegarlo
                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read() + "\n")
                except Exception as e:
                    outfile.write(f"// No se pudo leer este archivo: {e}\n")

print(f"¡Listo! Todo tu código se unificó en el archivo: {archivo_salida}")