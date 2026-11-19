# ClasificadorImagenes · Agente maestro

> Clasificador visual de imágenes estilo "swipe": derecha para aceptar, izquierda para rechazar.

## Qué hace

Eliges una carpeta con imágenes y la app crea tres subcarpetas dentro de ella:

| Carpeta | Contenido |
|---|---|
| `WEval/` | Imágenes pendientes de evaluar (la app mueve aquí las de la carpeta raíz) |
| `Accepted/` | Las que arrastraste a la derecha o aceptaste con `→` |
| `Reject/` | Las que arrastraste a la izquierda o rechazaste con `←` |

Muestra una imagen a la vez y la **mueve** físicamente a la carpeta correspondiente. Sirve para depurar rápido grandes lotes de fotos (por ejemplo, un dataset).

## Estado

**Funcional, dos versiones.** Última modificación: 23-feb-2026.

## Cómo se usa

```powershell
.\.venv\Scripts\activate              # entorno con Python 3.13.1
python clasificationPythonModern.py   # versión PySide6 con temas
python clasificationPython.py         # versión Tkinter clásica
```

## Archivos clave

| Archivo | Función |
|---|---|
| `clasificationPythonModern.py` | Versión moderna en PySide6: tarjeta arrastrable con animación y 5 temas de color (Tinder, Bumble, Hinge, Grindr, Badoo) |
| `clasificationPython.py` | Versión Tkinter: 3 columnas con flechas laterales animadas y carga de imágenes en hilo aparte |

## Dependencias

En `requirements.txt`, probadas en `.venv/` (Python 3.13.1, ~830 MB, casi todo PySide6): `PySide6 6.10.2` (solo la versión moderna), `polars 1.38.1` (lista de imágenes), `Pillow 12.1.1`.

## Cambios del 19-nov-2026

- Se agregó `requirements.txt`. Los dos scripts ya tenían descripción al inicio.

## Observaciones y pendientes

- Las imágenes se **mueven**, no se copian: conviene trabajar sobre una copia del lote.
- No hay botón de deshacer.
- Hay dos versiones con la misma lógica; decidir cuál queda como principal.
- `polars` se usa solo para guardar la lista de rutas; una lista normal de Python bastaría.

## Reglas para el agente

- Respetar los nombres de carpeta `WEval`, `Accepted`, `Reject`: el usuario ya tiene lotes organizados así.
- Cualquier cambio que toque archivos del usuario debe evitar sobrescribir una imagen con el mismo nombre en el destino.
