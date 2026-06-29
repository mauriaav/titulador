"""
hotkey_manager.py
-----------------
Responsabilidad: registrar y gestionar el atajo de teclado global.
"""

import threading
from typing import Callable


class HotkeyManager:
    """
    Registra un atajo de teclado global que ejecuta un callback.

    Usa la librería `keyboard` que funciona a nivel sistema operativo,
    por lo que el atajo responde incluso con otra ventana en primer plano.

    Parámetros
    ----------
    combinacion : str
        Atajo en formato keyboard, ej: "ctrl+shift+space"
    callback : Callable
        Función a ejecutar cuando se presiona el atajo.
    """

    def __init__(self, combinacion: str, callback: Callable):
        self.combinacion = combinacion
        self._callback   = callback
        self._activo     = False

    def iniciar(self) -> None:
        """Registra el hotkey en un hilo separado para no bloquear la UI."""
        try:
            import keyboard
        except ImportError:
            raise ImportError("Instalá keyboard: pip install keyboard")

        keyboard.add_hotkey(self.combinacion, self._callback, suppress=True)
        self._activo = True

        # keyboard.wait() necesita correr en hilo propio para no bloquear Tkinter
        self._hilo = threading.Thread(target=keyboard.wait, daemon=True)
        self._hilo.start()

    def detener(self) -> None:
        """Elimina el hotkey registrado."""
        if self._activo:
            try:
                import keyboard
                keyboard.remove_hotkey(self.combinacion)
            except Exception:
                pass
            self._activo = False

    def __repr__(self) -> str:
        estado = "activo" if self._activo else "inactivo"
        return f"HotkeyManager('{self.combinacion}', {estado})"
