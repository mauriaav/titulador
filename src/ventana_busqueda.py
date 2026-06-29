"""
ventana_busqueda.py
-------------------
Responsabilidad: UI de búsqueda y selección de títulos.
"""

import tkinter as tk
from tkinter import font as tkfont

from .titulo_manager import TituloManager


# Paleta de colores
COLORES = {
    "fondo":          "#1e1e2e",
    "fondo_entrada":  "#2a2a3e",
    "fondo_lista":    "#1e1e2e",
    "seleccion":      "#7c3aed",
    "seleccion_fg":   "#ffffff",
    "texto":          "#e2e8f0",
    "texto_suave":    "#94a3b8",
    "borde":          "#7c3aed",
    "hover":          "#2d2d44",
    "exito":          "#22c55e",
}


class VentanaBusqueda(tk.Toplevel):
    """
    Ventana flotante de búsqueda de títulos.

    Al seleccionar un ítem (clic o Enter) copia el texto al portapapeles
    y se cierra automáticamente.

    Parámetros
    ----------
    parent : tk.Tk
        Ventana raíz (oculta) de la aplicación.
    manager : TituloManager
        Instancia con los títulos cargados.
    on_seleccion : callable, opcional
        Callback que recibe el título seleccionado (para notificaciones, etc.)
    """

    ANCHO = 520
    ALTO  = 420
    MAX_VISIBLE = 8

    def __init__(self, parent: tk.Tk, manager: TituloManager, on_seleccion=None):
        super().__init__(parent)
        self._manager = manager
        self._on_seleccion = on_seleccion
        self._indice_hover = -1

        self._configurar_ventana()
        self._construir_ui()
        self._centrar()
        self._actualizar_lista("")

        # Foco en el buscador al abrir
        self.after(50, self._entrada.focus_set)

    # ------------------------------------------------------------------
    # Configuración inicial
    # ------------------------------------------------------------------

    def _configurar_ventana(self) -> None:
        self.title("ClipTítulos")
        self.resizable(False, False)
        self.configure(bg=COLORES["fondo"])
        self.overrideredirect(True)       # Sin barra de título del SO
        self.attributes("-topmost", True) # Siempre encima

        # Cierre con Escape
        self.bind("<Escape>", lambda _: self.destroy())
        # Cierre al perder el foco
        self.bind("<FocusOut>", self._on_foco_perdido)

    def _construir_ui(self) -> None:
        fuente_entrada = tkfont.Font(family="Segoe UI", size=13)
        fuente_item    = tkfont.Font(family="Segoe UI", size=11)
        fuente_info    = tkfont.Font(family="Segoe UI", size=9)

        # ── Contenedor principal con borde ──────────────────────────────
        marco = tk.Frame(self, bg=COLORES["borde"], padx=2, pady=2)
        marco.pack(fill="both", expand=True)

        interior = tk.Frame(marco, bg=COLORES["fondo"])
        interior.pack(fill="both", expand=True)

        # ── Cabecera ────────────────────────────────────────────────────
        cabecera = tk.Frame(interior, bg=COLORES["fondo_entrada"], pady=10)
        cabecera.pack(fill="x", padx=0)

        tk.Label(
            cabecera, text="🔍 ClipTítulos",
            bg=COLORES["fondo_entrada"], fg=COLORES["texto_suave"],
            font=tkfont.Font(family="Segoe UI", size=9, weight="bold")
        ).pack(side="left", padx=14)

        # ── Entrada de búsqueda ─────────────────────────────────────────
        frame_entrada = tk.Frame(interior, bg=COLORES["fondo"], pady=10)
        frame_entrada.pack(fill="x", padx=12)

        self._var_busqueda = tk.StringVar()
        self._var_busqueda.trace_add("write", self._on_texto_cambiado)

        self._entrada = tk.Entry(
            frame_entrada,
            textvariable=self._var_busqueda,
            font=fuente_entrada,
            bg=COLORES["fondo_entrada"],
            fg=COLORES["texto"],
            insertbackground=COLORES["texto"],
            relief="flat",
            bd=8,
        )
        self._entrada.pack(fill="x")
        self._entrada.bind("<Down>",   self._navegar_abajo)
        self._entrada.bind("<Up>",     self._navegar_arriba)
        self._entrada.bind("<Return>", self._seleccionar_actual)

        # ── Lista de resultados (Canvas + Scrollbar) ────────────────────
        frame_lista = tk.Frame(interior, bg=COLORES["fondo"])
        frame_lista.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        scrollbar = tk.Scrollbar(frame_lista, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            frame_lista,
            font=fuente_item,
            bg=COLORES["fondo_lista"],
            fg=COLORES["texto"],
            selectbackground=COLORES["seleccion"],
            selectforeground=COLORES["seleccion_fg"],
            activestyle="none",
            relief="flat",
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            height=self.MAX_VISIBLE,
        )
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._listbox.yview)

        self._listbox.bind("<ButtonRelease-1>", self._seleccionar_click)
        self._listbox.bind("<Return>",          self._seleccionar_actual)
        self._listbox.bind("<Double-Button-1>", self._seleccionar_click)

        # ── Pie: contador de resultados y atajo ─────────────────────────
        pie = tk.Frame(interior, bg=COLORES["fondo_entrada"], pady=6)
        pie.pack(fill="x", side="bottom")

        self._lbl_contador = tk.Label(
            pie, text="",
            bg=COLORES["fondo_entrada"], fg=COLORES["texto_suave"],
            font=fuente_info
        )
        self._lbl_contador.pack(side="left", padx=14)

        tk.Label(
            pie, text="↑↓ navegar  •  Enter / clic para copiar  •  Esc cerrar",
            bg=COLORES["fondo_entrada"], fg=COLORES["texto_suave"],
            font=fuente_info
        ).pack(side="right", padx=14)

    # ------------------------------------------------------------------
    # Lógica de búsqueda y lista
    # ------------------------------------------------------------------

    def _on_texto_cambiado(self, *_) -> None:
        query = self._var_busqueda.get()
        self._actualizar_lista(query)

    def _actualizar_lista(self, query: str) -> None:
        resultados = self._manager.buscar(query)
        self._listbox.delete(0, "end")
        for titulo in resultados:
            self._listbox.insert("end", f"  {titulo}")

        total = len(resultados)
        self._lbl_contador.config(
            text=f"{total} resultado{'s' if total != 1 else ''}"
        )

        if total > 0:
            self._listbox.selection_set(0)

    # ------------------------------------------------------------------
    # Navegación con teclado
    # ------------------------------------------------------------------

    def _navegar_abajo(self, _=None) -> None:
        self._listbox.focus_set()
        actual = self._listbox.curselection()
        siguiente = (actual[0] + 1) if actual else 0
        if siguiente < self._listbox.size():
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(siguiente)
            self._listbox.see(siguiente)

    def _navegar_arriba(self, _=None) -> None:
        actual = self._listbox.curselection()
        if not actual:
            return
        anterior = actual[0] - 1
        if anterior >= 0:
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(anterior)
            self._listbox.see(anterior)
        else:
            self._entrada.focus_set()

    # ------------------------------------------------------------------
    # Selección y copia
    # ------------------------------------------------------------------

    def _seleccionar_click(self, _=None) -> None:
        sel = self._listbox.curselection()
        if sel:
            self._copiar_y_cerrar(self._listbox.get(sel[0]).strip())

    def _seleccionar_actual(self, _=None) -> None:
        sel = self._listbox.curselection()
        if sel:
            self._copiar_y_cerrar(self._listbox.get(sel[0]).strip())

    def _copiar_y_cerrar(self, titulo: str) -> None:
        """Copia el título al portapapeles y cierra la ventana."""
        self.clipboard_clear()
        self.clipboard_append(titulo)
        self.update()  # Necesario para que Tkinter confirme el clipboard

        if self._on_seleccion:
            self._on_seleccion(titulo)

        self.destroy()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def _centrar(self) -> None:
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        ancho_pantalla  = self.winfo_screenwidth()
        alto_pantalla   = self.winfo_screenheight()
        x = (ancho_pantalla  - self.ANCHO) // 2
        y = (alto_pantalla   - self.ALTO)  // 3  # Un poco más arriba del centro
        self.geometry(f"{self.ANCHO}x{self.ALTO}+{x}+{y}")

    def _on_foco_perdido(self, evento) -> None:
        """Cierra si el foco pasa a otra aplicación (no a widgets internos)."""
        widget_con_foco = self.focus_get()
        if widget_con_foco is None:
            self.after(100, self._verificar_foco)

    def _verificar_foco(self) -> None:
        if self.focus_get() is None:
            try:
                self.destroy()
            except tk.TclError:
                pass
