"""
main.py
-------
Punto de entrada de ClipTítulos.
Busca el CSV en la misma carpeta que el ejecutable.
"""

import sys
import os
from pathlib import Path


def obtener_ruta_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def redirigir_salida(base: Path) -> None:
    """
    Con --noconsole, sys.stdout y sys.stderr no existen.
    Los redirigimos a un archivo de log para no crashear con print().
    """
    if getattr(sys, "frozen", False):
        log_path = base / "cliptitulos.log"
        log = open(log_path, "a", encoding="utf-8", buffering=1)
        sys.stdout = log
        sys.stderr = log
        # stdin tampoco existe en --noconsole
        sys.stdin = open(os.devnull, "r")


def mostrar_error(mensaje: str) -> None:
    """Muestra un error con messagebox (no usa consola)."""
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("ClipTítulos — Error", mensaje)
    root.destroy()


def main():
    base = obtener_ruta_base()
    redirigir_salida(base)

    ruta_csv = base / "data" / "titulos.csv"

    if not ruta_csv.exists():
        ruta_xlsx = base / "data" / "titulos.xlsx"
        if ruta_xlsx.exists():
            ruta_csv = ruta_xlsx
        else:
            mostrar_error(
                f"No se encontró el archivo de títulos.\n\n"
                f"Ubicación esperada:\n{ruta_csv}\n\n"
                f"Creá un CSV o Excel en la carpeta 'data\\' con una columna 'titulo'."
            )
            sys.exit(1)

    from src.app import ClipTitulosApp

    app = ClipTitulosApp(
        ruta_csv=ruta_csv,
        hotkey="ctrl+shift+space",
    )
    app.ejecutar()


if __name__ == "__main__":
    main()
