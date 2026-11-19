"""
Clasificador Visual Rápido de Imágenes
Versión Ultra-optimizada con Polars y Tkinter
Windows 11 - Máxima calidad y rendimiento
Estructura de 3 columnas con flechas laterales
"""

import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import polars as pl
from PIL import Image, ImageTk
import threading
from queue import Queue

class ClasificadorImagenes:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Clasificador Visual Rápido")
        self.root.geometry("1400x900")
        
        # Configurar estilo moderno
        self.setup_styles()
        
        # Variables de control
        self.carpeta_raiz = None
        self.df_imagenes = None
        self.indice_actual = 0
        self.image_tk = None
        self.cola_carga = Queue(maxsize=3)
        
        # Variables para animación
        self.animacion_activa = False
        self.direccion_animacion = None
        
        # Rutas de carpetas
        self.weval_path = None
        self.accepted_path = None
        self.reject_path = None
        
        # Bindings
        self.drag_start_x = 0
        self.procesando = False
        
        self.crear_interfaz()
        self.setup_atajos()
        
    def setup_styles(self):
        """Configura estilos modernos"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Info.TLabel', font=('Segoe UI', 11))
        style.configure('Arrow.TLabel', font=('Segoe UI', 14, 'bold'))
        
    def crear_interfaz(self):
        """Crea interfaz con estructura de 3 columnas"""
        # Header (sin cambios)
        header = ttk.Frame(self.root, padding="15")
        header.pack(fill=tk.X)
        
        ttk.Label(header, text="📸 Clasificador Visual Rápido", 
                 style='Title.TLabel').pack(side=tk.LEFT, padx=10)
        
        self.btn_cargar = ttk.Button(header, text="📂 Seleccionar Carpeta Raíz",
                                     command=self.seleccionar_carpeta,
                                     style='Info.TLabel')
        self.btn_cargar.pack(side=tk.RIGHT, padx=10)
        
        # Frame de información
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill=tk.X)
        
        self.lbl_carpeta = ttk.Label(info_frame, text="📁 No hay carpeta seleccionada", 
                                     style='Info.TLabel')
        self.lbl_carpeta.pack(side=tk.LEFT, padx=10)
        
        self.lbl_progreso = ttk.Label(info_frame, text="0/0 imágenes", 
                                      style='Info.TLabel')
        self.lbl_progreso.pack(side=tk.RIGHT, padx=10)
        
        # --- ESTRUCTURA DE 3 COLUMNAS ---
        self.columns_frame = ttk.Frame(self.root)
        self.columns_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Configurar grid para 3 columnas
        self.columns_frame.grid_columnconfigure(0, weight=1)  # Columna izquierda
        self.columns_frame.grid_columnconfigure(1, weight=8)  # Columna central (imagen)
        self.columns_frame.grid_columnconfigure(2, weight=1)  # Columna derecha
        self.columns_frame.grid_rowconfigure(0, weight=1)
        
        # COLUMNA IZQUIERDA - Flecha Reject
        self.left_frame = ttk.Frame(self.columns_frame)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Centrar contenido verticalmente
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=1)
        
        # Flecha izquierda (Reject)
        self.left_arrow_frame = ttk.Frame(self.left_frame)
        self.left_arrow_frame.grid(row=1, column=0)
        
        # Canvas para flecha izquierda
        self.left_canvas = tk.Canvas(self.left_arrow_frame, width=100, height=150, 
                                     bg='#2b2b2b', highlightthickness=0)
        self.left_canvas.pack()
        
        # Dibujar flecha izquierda
        self.left_canvas.create_polygon(70, 40, 30, 75, 70, 110, 
                                        fill='#F44336', outline='white', width=2)
        self.left_canvas.create_text(50, 130, text="RECHAZAR", fill='white', 
                                     font=('Segoe UI', 10, 'bold'))
        
        # COLUMNA CENTRAL - Imagen
        self.center_frame = ttk.Frame(self.columns_frame)
        self.center_frame.grid(row=0, column=1, sticky='nsew')
        
        # Frame para la imagen (contenedor)
        self.image_container = ttk.Frame(self.center_frame)
        self.image_container.pack(expand=True, fill=tk.BOTH)
        
        # Label para la imagen
        self.lbl_imagen = ttk.Label(self.image_container, background='#2b2b2b')
        self.lbl_imagen.pack(expand=True, fill=tk.BOTH)
        
        # COLUMNA DERECHA - Flecha Accept
        self.right_frame = ttk.Frame(self.columns_frame)
        self.right_frame.grid(row=0, column=2, sticky='nsew', padx=(10, 0))
        
        # Centrar contenido verticalmente
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)
        
        # Flecha derecha (Accept)
        self.right_arrow_frame = ttk.Frame(self.right_frame)
        self.right_arrow_frame.grid(row=1, column=0)
        
        # Canvas para flecha derecha
        self.right_canvas = tk.Canvas(self.right_arrow_frame, width=100, height=150, 
                                      bg='#2b2b2b', highlightthickness=0)
        self.right_canvas.pack()
        
        # Dibujar flecha derecha
        self.right_canvas.create_polygon(30, 40, 70, 75, 30, 110, 
                                         fill='#4CAF50', outline='white', width=2)
        self.right_canvas.create_text(50, 130, text="ACEPTAR", fill='white', 
                                      font=('Segoe UI', 10, 'bold'))
        
        # Footer (instrucciones)
        footer = ttk.Frame(self.root, padding="15")
        footer.pack(fill=tk.X)
        
        instrucciones = """
        🖱️ ARRASTRA: Imagen hacia la DERECHA (Aceptar) | Imagen hacia la IZQUIERDA (Rechazar)
        ⌨️ TECLADO: → Aceptar | ← Rechazar
        """
        ttk.Label(footer, text=instrucciones, style='Info.TLabel',
                 justify=tk.CENTER).pack()
        
        # Bindings
        self.lbl_imagen.bind('<B1-Motion>', self.on_drag)
        self.lbl_imagen.bind('<ButtonRelease-1>', self.on_drop)
        self.root.bind('<Configure>', self.on_window_resize)
        
    def animar_flecha(self, direccion, paso=0):
        """Anima la flecha correspondiente"""
        if paso < 6:  # 3 parpadeos
            canvas = self.left_canvas if direccion == 'reject' else self.right_canvas
            
            if paso % 2 == 0:
                # Resaltar flecha
                if direccion == 'reject':
                    self.left_canvas.itemconfig(1, fill='#FF6666')
                else:
                    self.right_canvas.itemconfig(1, fill='#66BB66')
            else:
                # Volver a color normal
                if direccion == 'reject':
                    self.left_canvas.itemconfig(1, fill='#F44336')
                else:
                    self.right_canvas.itemconfig(1, fill='#4CAF50')
            
            self.root.after(150, lambda: self.animar_flecha(direccion, paso + 1))
        else:
            # Restaurar colores
            self.left_canvas.itemconfig(1, fill='#F44336')
            self.right_canvas.itemconfig(1, fill='#4CAF50')
            # Ejecutar clasificación
            self.clasificar_actual(direccion)
        
    def setup_atajos(self):
        """Configura atajos de teclado"""
        self.root.bind('<Right>', lambda e: self.animar_flecha('accepted', 0))
        self.root.bind('<Left>', lambda e: self.animar_flecha('reject', 0))
        
    def on_window_resize(self, event):
        """Maneja redimensionamiento"""
        if hasattr(self, 'image_tk') and self.image_tk:
            self.mostrar_imagen_actual()
        
    def seleccionar_carpeta(self):
        """Selecciona carpeta raíz"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta raíz")
        
        if carpeta:
            self.carpeta_raiz = Path(carpeta)
            self.lbl_carpeta.config(text=f"📁 {self.carpeta_raiz.name}")
            
            # Crear estructura
            self.crear_estructura_carpetas()
            
            # Solo mover si WEval está vacío
            if not any(self.weval_path.iterdir()):
                self.mover_imagenes_a_weval()
            else:
                print("📂 WEval ya contiene imágenes, continuando...")
            
            # Cargar imágenes
            self.cargar_imagenes_optimizado()
    
    def crear_estructura_carpetas(self):
        """Crea las 3 carpetas"""
        self.weval_path = self.carpeta_raiz / "WEval"
        self.accepted_path = self.carpeta_raiz / "Accepted"
        self.reject_path = self.carpeta_raiz / "Reject"
        
        for path in [self.weval_path, self.accepted_path, self.reject_path]:
            path.mkdir(exist_ok=True)
    
    def mover_imagenes_a_weval(self):
        """Mueve solo imágenes válidas a WEval"""
        extensiones = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
        movidas = 0
        ignorados = 0
        
        for archivo in self.carpeta_raiz.iterdir():
            if archivo.is_file():
                if archivo.suffix.lower() in extensiones:
                    destino = self.weval_path / archivo.name
                    if not destino.exists():
                        shutil.move(str(archivo), str(destino))
                        movidas += 1
                else:
                    ignorados += 1
                    print(f"⏭️ Ignorado: {archivo.name}")
        
        if movidas > 0:
            print(f"✅ {movidas} imágenes movidas a WEval")
        if ignorados > 0:
            print(f"⏭️ {ignorados} archivos ignorados")
    
    def cargar_imagenes_optimizado(self):
        """Carga imágenes desde WEval"""
        if not self.weval_path or not self.weval_path.exists():
            return
        
        extensiones = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        
        imagenes = []
        for ext in extensiones:
            imagenes.extend(self.weval_path.glob(f'*{ext}'))
            imagenes.extend(self.weval_path.glob(f'*{ext.upper()}'))
        
        if imagenes:
            datos = [{
                'ruta': str(img),
                'nombre': img.name
            } for img in imagenes]
            
            self.df_imagenes = pl.DataFrame(datos).sort('nombre')
            self.indice_actual = 0
            
            print(f"📊 Cargadas {len(self.df_imagenes)} imágenes")
            self.mostrar_imagen_actual()
        else:
            self.mostrar_mensaje_sin_imagenes()
    
    def mostrar_mensaje_sin_imagenes(self):
        """Muestra mensaje cuando no hay imágenes"""
        self.lbl_imagen.config(
            image='', 
            text='📭 No quedan más imágenes por clasificar', 
            font=('Segoe UI', 20), 
            foreground='#888888'
        )
        self.lbl_progreso.config(text="0/0 imágenes")
        
    def mostrar_imagen_actual(self):
        """Muestra la imagen actual adaptada"""
        if self.df_imagenes is None or len(self.df_imagenes) == 0:
            self.mostrar_mensaje_sin_imagenes()
            return
        
        if self.indice_actual < len(self.df_imagenes):
            ruta_imagen = self.df_imagenes[self.indice_actual, 'ruta']
            
            self.lbl_progreso.config(
                text=f"{self.indice_actual + 1}/{len(self.df_imagenes)} imágenes"
            )
            
            threading.Thread(target=self.cargar_imagen_adaptada, 
                           args=(ruta_imagen,), daemon=True).start()
    
    def cargar_imagen_adaptada(self, ruta):
        """Carga imagen adaptada al contenedor central"""
        try:
            # Cargar imagen original
            imagen = Image.open(ruta)
            
            # Obtener dimensiones del contenedor central
            ancho_cont = self.center_frame.winfo_width()
            alto_cont = self.center_frame.winfo_height()
            
            if ancho_cont < 100:
                ancho_cont = 800
                alto_cont = 600
            
            # Calcular nuevo tamaño manteniendo aspecto
            img_ancho, img_alto = imagen.size
            proporcion = min(ancho_cont/img_ancho, alto_cont/img_alto)
            
            nuevo_ancho = int(img_ancho * proporcion)
            nuevo_alto = int(img_alto * proporcion)
            
            # Redimensionar con alta calidad
            imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            
            self.image_tk = ImageTk.PhotoImage(imagen)
            
            # Actualizar interfaz
            self.root.after(0, self.actualizar_imagen_interfaz)
            
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            self.root.after(0, self.siguiente_imagen)
    
    def actualizar_imagen_interfaz(self):
        """Actualiza la imagen en la interfaz"""
        if self.image_tk:
            self.lbl_imagen.config(image=self.image_tk, text='')
            self.lbl_imagen.image = self.image_tk
    
    def on_drag(self, event):
        """Registra inicio del arrastre"""
        self.drag_start_x = event.x_root
        
    def on_drop(self, event):
        """Procesa el gesto de arrastre"""
        if hasattr(self, 'drag_start_x') and not self.procesando:
            diferencia = event.x_root - self.drag_start_x
            
            if abs(diferencia) > 100:
                self.procesando = True
                if diferencia > 0:
                    self.animar_flecha('accepted', 0)
                else:
                    self.animar_flecha('reject', 0)
    
    def clasificar_actual(self, destino):
        """Clasifica la imagen actual"""
        if self.df_imagenes is None or self.indice_actual >= len(self.df_imagenes):
            self.procesando = False
            return
        
        ruta_origen = self.df_imagenes[self.indice_actual, 'ruta']
        nombre = self.df_imagenes[self.indice_actual, 'nombre']
        
        if destino == 'accepted':
            ruta_destino = self.accepted_path / nombre
        else:
            ruta_destino = self.reject_path / nombre
        
        try:
            shutil.move(ruta_origen, str(ruta_destino))
            print(f"{'✅' if destino=='accepted' else '❌'} {nombre}")
            
            self.df_imagenes = self.df_imagenes.filter(
                pl.col('ruta') != ruta_origen
            )
            
            self.procesando = False
            
            if len(self.df_imagenes) > 0:
                self.mostrar_imagen_actual()
            else:
                self.mostrar_mensaje_sin_imagenes()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mover {nombre}")
            self.procesando = False
    
    def siguiente_imagen(self):
        """Avanza a siguiente imagen"""
        self.procesando = False
        self.mostrar_imagen_actual()

def main():
    root = tk.Tk()
    app = ClasificadorImagenes(root)
    root.mainloop()

if __name__ == "__main__":
    main()