import os

# Excluimos directorios de assets, entornos virtuales y caché
IGNORAR_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "alembic",
    ".flet",
    "build",
    ".pytest_cache",
    "assets",
    "scripts",
}

# Extensiones estrictamente de texto y código
EXTENSIONES = {".py", ".pgsql", ".sql", ".md", ".toml"}

archivo_salida = "proyecto_completo_limpio.txt"

directorio_raiz = os.path.dirname(os.path.abspath(__file__))

with open(archivo_salida, "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk(directorio_raiz):
        # Filtramos carpetas en tiempo real
        dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS]

        for file in files:
            # Filtramos por extensión y evitamos que se lea a sí mismo o el archivo de salida
            if any(file.endswith(ext) for ext in EXTENSIONES) and file not in [
                os.path.basename(__file__),
                archivo_salida,
            ]:
                filepath = os.path.join(root, file)
                ruta_relativa = os.path.relpath(filepath, directorio_raiz)

                # Intentamos leer forzando UTF-8 y manejando errores de codificación
                try:
                    with open(
                        filepath, "r", encoding="utf-8", errors="ignore"
                    ) as infile:
                        contenido = infile.read()

                        # Control de seguridad: Si el archivo contiene bytes nulos (clásico de binarios o ZIPs), lo omitimos
                        if "\x00" in contenido:
                            continue

                        outfile.write(f"\n{'=' * 70}\n")
                        outfile.write(f"--- RUTA: {ruta_relativa} ---\n")
                        outfile.write(f"{'=' * 70}\n\n")
                        outfile.write(contenido + "\n")

                except Exception as e:
                    outfile.write(f"// No se pudo leer {ruta_relativa}: {e}\n")

print(f"¡Extracción exitosa! Revisa el archivo: {archivo_salida}")
