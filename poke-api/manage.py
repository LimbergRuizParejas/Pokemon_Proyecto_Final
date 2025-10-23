#!/usr/bin/env python3
"""
Django management utility for administrative tasks.

Este script actúa como punto de entrada para todas las tareas de administración
del proyecto Django (migraciones, servidor local, creación de usuarios, etc.).
"""

import os
import sys
from pathlib import Path


def main():
    """
    Ejecuta las tareas administrativas del proyecto Django.
    Detecta automáticamente el entorno (desarrollo o producción)
    y lanza los comandos con un manejo de errores más claro.
    """
    # Ruta base del proyecto
    BASE_DIR = Path(__file__).resolve().parent

    # Detectar entorno (si existe un archivo .env.prod o variable ENV)
    environment = os.environ.get("DJANGO_ENV", "development").lower()

    if environment == "production":
        settings_module = "poke_api.settings.production"
    else:
        settings_module = "poke_api.settings"  # fallback por defecto

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    # Activar color en Windows (mejor experiencia CLI)
    if sys.platform == "win32":
        try:
            import colorama
            colorama.just_fix_windows_console()
        except ImportError:
            pass  # no es obligatorio, solo mejora visual

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "❌ No se pudo importar Django. "
            "Verifica que esté instalado y que tu entorno virtual esté activado.\n\n"
            "👉 Solución: ejecuta\n"
            "   python -m venv venv\n"
            "   venv\\Scripts\\activate (Windows)\n"
            "   pip install -r requirements.txt"
        ) from exc

    # Si no se pasan argumentos, mostrar ayuda básica
    if len(sys.argv) == 1:
        print("\n🧩 Uso: python manage.py <comando>\n")
        print("Comandos comunes:")
        print("  runserver         Inicia el servidor de desarrollo")
        print("  makemigrations    Crea nuevas migraciones de base de datos")
        print("  migrate           Aplica las migraciones a la base de datos")
        print("  createsuperuser   Crea un usuario administrador\n")
        print("Ejemplo:")
        print("  python manage.py runserver\n")

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
