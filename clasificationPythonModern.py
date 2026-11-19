"""
Clasificador Visual Rápido de Imágenes
PySide6 + Swipe tipo Tinder
Sistema de temas: Tinder / Bumble / Hinge / Grindr / Badoo
Archivo único
"""

import sys
import shutil
from pathlib import Path
import polars as pl
from PIL import Image

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox
)
from PySide6.QtCore import (
    Qt, QPoint, QPropertyAnimation, QEasingCurve, QSize
)
from PySide6.QtGui import QPixmap, QImage, QFont


# ---------- TEMAS ----------
THEMES = {
    "Tinder": {
        "primary": "#FF4458",
        "secondary": "#FFFFFF",
        "background": "#111111",
        "card_bg": "#1A1A1A",
        "gradient_start": "#FD5068",
        "gradient_end": "#FF6036",
        "text": "#FFFFFF",
        "font": "Segoe UI"
    },
    "Bumble": {
        "primary": "#F7B500",
        "secondary": "#000000",
        "background": "#FFF8E1",
        "card_bg": "#FFFFFF",
        "gradient_start": "#F7B500",
        "gradient_end": "#FFE082",
        "text": "#000000",
        "font": "Segoe UI"
    },
    "Hinge": {
        "primary": "#6A4C93",
        "secondary": "#FFFFFF",
        "background": "#F6F6F6",
        "card_bg": "#FFFFFF",
        "gradient_start": "#6A4C93",
        "gradient_end": "#8E6CC7",
        "text": "#2D2D2D",
        "font": "Segoe UI"
    },
    "Grindr": {
        "primary": "#F2A900",
        "secondary": "#FFFFFF",
        "background": "#000000",
        "card_bg": "#1A1A1A",
        "gradient_start": "#F2A900",
        "gradient_end": "#FFD24A",
        "text": "#FFFFFF",
        "font": "Segoe UI"
    },
    "Badoo": {
        "primary": "#783BF9",
        "secondary": "#FFFFFF",
        "background": "#EDE7FF",
        "card_bg": "#FFFFFF",
        "gradient_start": "#783BF9",
        "gradient_end": "#A178FF",
        "text": "#2E2E2E",
        "font": "Segoe UI"
    }
}


# ---------- WIDGET TARJETA SWIPE ----------
class ImageCard(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(600, 500)

        self.drag_start = None
        self.callback_accept = None
        self.callback_reject = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.drag_start:
            return

        delta = event.globalPosition().toPoint() - self.drag_start
        self.move(self.pos() + QPoint(delta.x(), 0))
        self.drag_start = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if not self.drag_start:
            return

        threshold = 150
        center_x = self.parent().width() // 2
        diff = self.x() - center_x

        if diff > threshold:
            self.swipe("accepted")
        elif diff < -threshold:
            self.swipe("reject")
        else:
            self.reset_position()

        self.drag_start = None

    def reset_position(self):
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(200)
        anim.setEndValue(self.parent().rect().center() - self.rect().center())
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self.anim = anim

    def swipe(self, direction):
        end_x = self.x() + 900 if direction == "accepted" else self.x() - 900

        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(300)
        anim.setEndValue(QPoint(end_x, self.y()))
        anim.setEasingCurve(QEasingCurve.InQuad)

        def finished():
            if direction == "accepted" and self.callback_accept:
                self.callback_accept()
            if direction == "reject" and self.callback_reject:
                self.callback_reject()

        anim.finished.connect(finished)
        anim.start()
        self.anim = anim


# ---------- APP PRINCIPAL ----------
class ClasificadorImagenes(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Clasificador Visual Rápido")
        self.resize(1400, 900)

        self.theme_name = "Tinder"
        self.theme = THEMES[self.theme_name]

        self.carpeta_raiz = None
        self.df_imagenes = None
        self.indice_actual = 0

        self.weval_path = None
        self.accepted_path = None
        self.reject_path = None

        self.setup_ui()
        self.apply_theme()

    # ---------- UI ----------
    def setup_ui(self):
        container = QWidget()
        self.setCentralWidget(container)

        self.layout = QVBoxLayout(container)

        header = QHBoxLayout()

        self.titulo = QLabel("Clasificador Visual Rápido")
        self.titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.addWidget(self.titulo)

        header.addStretch()

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(THEMES.keys())
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        header.addWidget(self.theme_selector)

        btn = QPushButton("Seleccionar Carpeta")
        btn.clicked.connect(self.seleccionar_carpeta)
        header.addWidget(btn)

        self.layout.addLayout(header)

        self.lbl_info = QLabel("No hay carpeta seleccionada")
        self.layout.addWidget(self.lbl_info)

        self.lbl_progreso = QLabel("0/0 imágenes")
        self.layout.addWidget(self.lbl_progreso)

        self.card_container = QWidget()
        container_layout = QVBoxLayout(self.card_container)
        container_layout.setAlignment(Qt.AlignCenter)

        self.card = ImageCard(self.card_container)
        container_layout.addWidget(self.card)

        self.layout.addWidget(self.card_container)

        instrucciones = QLabel("Arrastra → aceptar | Arrastra ← rechazar | ← → teclado")
        instrucciones.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(instrucciones)

        self.card.callback_accept = lambda: self.clasificar_actual("accepted")
        self.card.callback_reject = lambda: self.clasificar_actual("reject")

    # ---------- THEMES ----------
    def change_theme(self, name):
        self.theme_name = name
        self.theme = THEMES[name]
        self.apply_theme()

    def apply_theme(self):
        t = self.theme

        self.setStyleSheet(f"""
        QMainWindow {{
            background:{t['background']};
            color:{t['text']};
            font-family:{t['font']};
        }}

        QLabel {{
            color:{t['text']};
        }}

        QPushButton {{
            background:qlineargradient(
                x1:0,y1:0,x2:1,y2:0,
                stop:0 {t['gradient_start']},
                stop:1 {t['gradient_end']}
            );
            border:none;
            padding:10px;
            border-radius:8px;
            color:white;
            font-weight:bold;
        }}

        QComboBox {{
            padding:6px;
            border-radius:6px;
        }}
        """)

        self.card.setStyleSheet(
            f"background:{t['card_bg']};border-radius:16px;padding:10px;"
        )

    # ---------- CARPETA ----------
    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta raíz")
        if not carpeta:
            return

        self.carpeta_raiz = Path(carpeta)
        self.lbl_info.setText(self.carpeta_raiz.name)

        self.crear_estructura_carpetas()

        if not any(self.weval_path.iterdir()):
            self.mover_imagenes_a_weval()

        self.cargar_imagenes()

    def crear_estructura_carpetas(self):
        self.weval_path = self.carpeta_raiz / "WEval"
        self.accepted_path = self.carpeta_raiz / "Accepted"
        self.reject_path = self.carpeta_raiz / "Reject"

        for p in [self.weval_path, self.accepted_path, self.reject_path]:
            p.mkdir(exist_ok=True)

    def mover_imagenes_a_weval(self):
        extensiones = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff")

        for archivo in self.carpeta_raiz.iterdir():
            if archivo.is_file() and archivo.suffix.lower() in extensiones:
                destino = self.weval_path / archivo.name
                if not destino.exists():
                    shutil.move(str(archivo), str(destino))

    # ---------- CARGA ----------
    def cargar_imagenes(self):
        extensiones = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"]

        imagenes = []
        for ext in extensiones:
            imagenes.extend(self.weval_path.glob(f"*{ext}"))
            imagenes.extend(self.weval_path.glob(f"*{ext.upper()}"))

        if not imagenes:
            self.card.setText("No hay imágenes")
            return

        datos = [{"ruta": str(img), "nombre": img.name} for img in imagenes]
        self.df_imagenes = pl.DataFrame(datos).sort("nombre")
        self.indice_actual = 0

        self.mostrar_imagen_actual()

    def mostrar_imagen_actual(self):
        if self.df_imagenes is None or len(self.df_imagenes) == 0:
            self.card.setText("No quedan imágenes")
            return

        ruta = self.df_imagenes[self.indice_actual, "ruta"]

        img = Image.open(ruta).convert("RGB")

        qimg = QImage(
            img.tobytes(),
            img.width,
            img.height,
            img.width * 3,
            QImage.Format_RGB888
        )

        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(
            QSize(900, 700),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.card.setPixmap(pix)
        self.lbl_progreso.setText(
            f"{self.indice_actual + 1}/{len(self.df_imagenes)} imágenes"
        )

        self.reset_card_position()

    def reset_card_position(self):
        self.card.move(
            self.card_container.width() // 2 - self.card.width() // 2,
            self.card_container.height() // 2 - self.card.height() // 2
        )

    # ---------- CLASIFICACIÓN ----------
    def clasificar_actual(self, destino):
        if self.df_imagenes is None:
            return

        ruta = self.df_imagenes[self.indice_actual, "ruta"]
        nombre = self.df_imagenes[self.indice_actual, "nombre"]

        destino_path = (
            self.accepted_path if destino == "accepted"
            else self.reject_path
        ) / nombre

        try:
            shutil.move(ruta, str(destino_path))

            self.df_imagenes = self.df_imagenes.filter(pl.col("ruta") != ruta)

            if len(self.df_imagenes) > 0:
                self.indice_actual = 0
                self.mostrar_imagen_actual()
            else:
                self.card.setText("No quedan imágenes")

        except Exception as e:
            print("Error:", e)

    # ---------- TECLADO ----------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self.card.swipe("accepted")
        elif event.key() == Qt.Key_Left:
            self.card.swipe("reject")


# ---------- MAIN ----------
def main():
    app = QApplication(sys.argv)
    window = ClasificadorImagenes()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
