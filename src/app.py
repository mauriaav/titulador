"""
app.py
------
Responsabilidad: orquestar TituloManager, HotkeyManager, TrayManager y VentanaBusqueda.
Es el punto de entrada de la lógica de negocio.
"""

import tkinter as tk
from pathlib import Path

from .titulo_manager   import TituloManager
from .hotkey_manager   import HotkeyManager
from .tray_manager     import TrayManager
from .ventana_busqueda import VentanaBusqueda


class ClipTitulosApp:
    """
    Aplicación principal de ClipTítulos.

    Corre en segundo plano con ventana raíz oculta e ícono en el system tray.
    Al presionar el hotkey (o doble clic en el tray), abre VentanaBusqueda.

    Parámetros
    ----------
    ruta_csv : str | Path
        Ruta al archivo CSV o Excel con los títulos.
    hotkey : str
        Combinación de teclas, ej: "ctrl+shift+space"
    """

    def __init__(self, ruta_csv: str | Path, hotkey: str = "ctrl+shift+space"):
        self.ruta_csv = Path(ruta_csv)
        self.hotkey   = hotkey

        self._ventana_abierta = False

        # Ventana raíz oculta (necesaria para Tkinter)
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.title("ClipTítulos")

        # Carga de títulos
        self._manager = TituloManager(self.ruta_csv)
        print(f"✅ {len(self._manager)} títulos cargados desde '{self.ruta_csv.name}'")

        # Hotkey global
        self._hotkey_mgr = HotkeyManager(self.hotkey, self._abrir_ventana_thread_safe)
        self._hotkey_mgr.iniciar()
        print(f"⌨️  Hotkey registrado: {self.hotkey.upper()}")

        # System tray
        self._tray_mgr = TrayManager(
            on_abrir=self._abrir_ventana_thread_safe,
            on_salir=self._salir,
            tooltip=f"ClipTítulos  ({self.hotkey.upper()})",
        )
        self._tray_mgr.iniciar()
        print("🟢 ClipTítulos corriendo en el system tray. Presioná el atajo para buscar.\n")

    # ------------------------------------------------------------------
    # Control de la ventana de búsqueda
    # ------------------------------------------------------------------

    def _abrir_ventana_thread_safe(self) -> None:
        """
        Keyboard llama al callback desde un hilo secundario.
        Tkinter debe actualizarse desde el hilo principal, así que
        usamos `after` para programar la apertura en el loop principal.
        """
        self._root.after(0, self._abrir_ventana)

    def _abrir_ventana(self) -> None:
        """Abre la ventana de búsqueda si no hay una ya abierta."""
        if self._ventana_abierta:
            return

        self._ventana_abierta = True
        ventana = VentanaBusqueda(
            parent=self._root,
            manager=self._manager,
            on_seleccion=self._on_titulo_copiado,
        )
        ventana.protocol("WM_DELETE_WINDOW", self._on_ventana_cerrada)
        ventana.bind("<Destroy>", lambda _: self._on_ventana_cerrada())

    def _on_ventana_cerrada(self) -> None:
        self._ventana_abierta = False

    def _on_titulo_copiado(self, titulo: str) -> None:
        print(f"📋 Copiado: {titulo}")

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def _salir(self) -> None:
        """Cierra la aplicación limpiamente desde el menú del tray."""
        self._hotkey_mgr.detener()
        self._root.after(0, self._root.quit)
        print("\n🔴 ClipTítulos cerrado.")

    def ejecutar(self) -> None:
        """Inicia el loop principal de Tkinter."""
        try:
            self._root.mainloop()
        finally:
            self._hotkey_mgr.detener()
            self._tray_mgr.detener()

    def __repr__(self) -> str:
        return f"ClipTitulosApp(csv='{self.ruta_csv}', hotkey='{self.hotkey}')"
