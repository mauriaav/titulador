"""
tray_manager.py
---------------
Responsabilidad: gestionar el ícono en el system tray de Windows.
Provee menú contextual con opciones: Abrir y Salir.
"""

import threading
from typing import Callable

from PIL import Image, ImageDraw


def _crear_icono() -> Image.Image:
    """
    Genera el ícono del tray programáticamente (sin archivo externo).
    Un círculo violeta con una 'C' blanca — no requiere assets.
    """
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fondo circular violeta
    draw.ellipse([2, 2, size - 2, size - 2], fill="#7c3aed")

    # Letra "C" centrada (usando rectángulos como aproximación simple)
    # Arco superior
    draw.arc([14, 14, 50, 50], start=40, end=320, fill="white", width=7)

    return img


class TrayManager:
    """
    Gestiona el ícono en el system tray de Windows.

    Parámetros
    ----------
    on_abrir : Callable
        Callback para abrir la ventana de búsqueda (igual que el hotkey).
    on_salir : Callable
        Callback para cerrar la aplicación completamente.
    tooltip : str
        Texto que aparece al pasar el mouse sobre el ícono.
    """

    def __init__(self, on_abrir: Callable, on_salir: Callable, tooltip: str = "ClipTítulos"):
        self._on_abrir  = on_abrir
        self._on_salir  = on_salir
        self._tooltip   = tooltip
        self._icono     = None
        self._hilo      = None

    def iniciar(self) -> None:
        """Lanza el tray en un hilo separado para no bloquear Tkinter."""
        self._hilo = threading.Thread(target=self._correr, daemon=True)
        self._hilo.start()

    def detener(self) -> None:
        """Detiene el ícono del tray."""
        if self._icono:
            try:
                self._icono.stop()
            except Exception:
                pass

    def _correr(self) -> None:
        import pystray

        menu = pystray.Menu(
            pystray.MenuItem(
                "🔍  Abrir buscador",
                self._accion_abrir,
                default=True,        # Doble clic ejecuta esta acción
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "✖  Salir",
                self._accion_salir,
            ),
        )

        self._icono = pystray.Icon(
            name="cliptitulos",
            icon=_crear_icono(),
            title=self._tooltip,
            menu=menu,
        )
        self._icono.run()

    # ------------------------------------------------------------------
    # Acciones del menú
    # ------------------------------------------------------------------

    def _accion_abrir(self, icono, item) -> None:
        self._on_abrir()

    def _accion_salir(self, icono, item) -> None:
        self.detener()
        self._on_salir()

    def __repr__(self) -> str:
        return f"TrayManager(tooltip='{self._tooltip}')"
