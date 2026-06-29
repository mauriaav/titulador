# 📋 ClipTítulos

Selector de títulos estandarizados con búsqueda rápida.  
Se activa con un atajo de teclado y copia el texto seleccionado al portapapeles.

---

## 🚀 Uso para el usuario final

1. Ejecutar `ClipTitulos.exe`
2. El programa corre en segundo plano (no se ve nada)
3. Presionar **`Ctrl + Shift + Space`** en cualquier momento
4. Escribir parte del título a buscar
5. Hacer **clic** en el resultado (o navegar con ↑↓ y presionar Enter)
6. Pegar con **`Ctrl + V`** donde se necesite

---

## 📁 Estructura del proyecto

```
cliptitulos/
│
├── main.py                  # Punto de entrada
├── requirements.txt         # Dependencias Python
├── build.bat                # Script para generar el .exe
│
├── src/                     # Código fuente (paquete Python)
│   ├── __init__.py
│   ├── app.py               # Orquestador principal (ClipTitulosApp)
│   ├── titulo_manager.py    # Carga y búsqueda de títulos (TituloManager)
│   ├── hotkey_manager.py    # Hotkey global (HotkeyManager)
│   └── ventana_busqueda.py  # UI Tkinter (VentanaBusqueda)
│
└── data/
    └── titulos.csv          # ← ACÁ SE EDITAN LOS TÍTULOS
```

---

## ✏️ Actualizar los títulos

Editar el archivo **`data/titulos.csv`** con Excel o cualquier editor de texto.  
El archivo debe tener **exactamente una columna llamada `titulo`**:

```
titulo
Atención al Cliente
Gestión de Reclamos
Soporte Técnico Nivel 1
...
```

> También se puede usar un archivo **`titulos.xlsx`** con la misma estructura.

---

## 🛠️ Desarrollo

### Requisitos
- Python 3.10+
- Windows (para el hotkey global)

### Instalación del entorno
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Correr en desarrollo
```bash
python main.py
```
> Nota: en Windows puede requerir ejecutar como Administrador para el hotkey global.

### Generar el .exe
```bash
build.bat
```
El ejecutable queda en `dist/ClipTitulos.exe`.  
Para distribuir, copiar **`ClipTitulos.exe`** junto con la carpeta **`data/`**.

---

## 🏗️ Arquitectura (POO)

| Clase | Archivo | Responsabilidad |
|---|---|---|
| `ClipTitulosApp` | `app.py` | Orquestador. Inicializa y conecta los demás módulos. |
| `TituloManager` | `titulo_manager.py` | Carga títulos desde CSV/Excel y provee búsqueda. |
| `HotkeyManager` | `hotkey_manager.py` | Registra el atajo de teclado global del sistema. |
| `VentanaBusqueda` | `ventana_busqueda.py` | Ventana flotante de búsqueda (hereda de `tk.Toplevel`). |

---

## ⌨️ Atajos dentro de la ventana

| Tecla | Acción |
|---|---|
| Escribir | Filtra resultados en tiempo real |
| `↓` / `↑` | Navegar por la lista |
| `Enter` | Copiar el ítem seleccionado |
| `Clic` | Copiar el ítem clickeado |
| `Esc` | Cerrar sin copiar |
