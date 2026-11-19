# ClasificadorImagenes

Clasificador visual de imágenes por deslizamiento: **derecha para aceptar, izquierda para rechazar**. Sirve para depurar rápido lotes grandes de fotos o preparar datasets.

## Cómo funciona

Eliges una carpeta con imágenes y la app crea dentro tres subcarpetas:

| Carpeta | Contenido |
|---|---|
| `WEval/` | Imágenes pendientes (la app mueve aquí las que estén sueltas en la carpeta) |
| `Accepted/` | Las que aceptaste |
| `Reject/` | Las que rechazaste |

Muestra una imagen a la vez. Arrástrala a un lado o usa las flechas `→` (aceptar) y `←` (rechazar).

> ⚠️ Las imágenes se **mueven**, no se copian. Trabaja sobre una copia si no quieres alterar la carpeta original.

## Versiones

| Archivo | Interfaz |
|---|---|
| `clasificationPythonModern.py` | PySide6: tarjeta arrastrable con animación y 5 temas de color |
| `clasificationPython.py` | Tkinter: 3 columnas con flechas laterales animadas |

## Instalación y uso

Python 3.13:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

python clasificationPythonModern.py
```

Formatos admitidos: JPG, PNG, BMP, GIF, TIFF, WEBP.
