"""Parchea el template de build de Flet 0.86.5 para poder generar el APK.

Problema: el template de Flet 0.86.5 fija `jni: 1.0.0` como
dependency_override de Flutter, pero `shared_preferences_android >= 2.5.4`
y `jni_flutter >= 1.0.4` (resueltos hoy desde pub.dev) traen bindings
generados que exigen `package:jni ^1.1.0`. La compilación falla con:

    Error: Constant evaluation error:
    const _$jniVersionCheck = jni$_.JniVersionCheck(1, 1);
    The generated bindings expect package:jni ^1.1.0, but 1.0.x was imported.

Solución: actualizar el pin del template cacheado a `jni: ^1.1.0`.

Uso (después de borrar el cache o en una máquina nueva):

    uv run python scripts/patch_flet_template.py

Se ejecuta automáticamente antes del build si el template sin parchear ya
está cacheado. Idempotente: si el template ya está parcheado, no hace nada.

Después de parchear, borrar `frontend/build/` para que `flet build` vuelva a
extraer el template desde el zip cacheado.
"""

import os
import shutil
import sys
import zipfile

import flet.version

ENTRY = "build/{{cookiecutter.out_dir}}/pubspec.yaml"
OLD = "jni: 1.0.0"
NEW = "jni: ^1.1.0"


def main() -> int:
    version = flet.version.flet_version
    zip_path = os.path.expanduser(
        f"~/.flet/cache/build-template/v{version}/flet-build-template.zip"
    )

    if not os.path.exists(zip_path):
        print(f"Template {zip_path} no encontrado: no hay nada que parchear.")
        print("(flet build lo descarga la primera vez; correr este script después.)")
        return 0

    with zipfile.ZipFile(zip_path) as z:
        pubspec = z.read(ENTRY).decode()

    if NEW in pubspec:
        print("El template ya está parcheado: nada que hacer.")
        return 0

    if OLD not in pubspec:
        print("El template no contiene el pin 'jni: 1.0.0' esperado;")
        print("revisar manualmente el pubspec del template.")
        return 1

    tmp_path = zip_path + ".patched"
    with (
        zipfile.ZipFile(zip_path, "r") as zin,
        zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout,
    ):
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == ENTRY:
                data = data.decode().replace(OLD, NEW).encode()
            zout.writestr(item, data)
    shutil.move(tmp_path, zip_path)

    print(f"Template v{version} parcheado: {OLD} -> {NEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
