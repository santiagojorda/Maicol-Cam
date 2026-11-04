import sys
import io
import os
import json
import cv2
import numpy as np

# Asegurar compatibilidad al ejecutar con pythonw (sin consola)
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QRectF, QTimer
from PyQt6.QtGui import QImage, QPainter, QPainterPath, QColor, QFont, QCursor, QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QMenu

def get_config_path():
    home_dir = os.path.expanduser("~")
    old_path = os.path.join(home_dir, "camara_flotante_config.json")
    new_path = os.path.join(home_dir, "maicol_cam_config.json")
    if not os.path.exists(new_path) and os.path.exists(old_path):
        return old_path
    return new_path

def load_config():
    cfg_path = get_config_path()
    if not os.path.exists(cfg_path):
        return None
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def get_app_icon_path():
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, '_MEIPASS', '')
        if meipass:
            p = os.path.join(meipass, "webcam.ico")
            if os.path.exists(p):
                return p
        exe_dir = os.path.dirname(sys.executable)
        p = os.path.join(exe_dir, "webcam.ico")
        if os.path.exists(p):
            return p

    script_dir = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(script_dir, "webcam.ico")
    if os.path.exists(p):
        return p

    p = os.path.join(os.path.expanduser("~"), "webcam.ico")
    if os.path.exists(p):
        return p

    return ""

class VideoCaptureThread(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    resolution_changed = pyqtSignal(int, int)

    def __init__(self, camera_index=0, target_width=1920, target_height=1080):
        super().__init__()
        self.camera_index = camera_index
        self.target_width = target_width
        self.target_height = target_height
        self._pending_camera = None
        self._pending_res = None
        self._run_flag = True

    def set_camera(self, new_index):
        self._pending_camera = new_index

    def set_resolution(self, width, height):
        self._pending_res = (width, height)

    def _open_camera(self):
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            return None

        # Configurar MJPG: permite 1080p y 720p a altos FPS sin saturar el bus USB de Windows
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.resolution_changed.emit(actual_w, actual_h)
        return cap

    def run(self):
        cap = self._open_camera()

        while self._run_flag:
            reopen_needed = False
            if self._pending_camera is not None:
                self.camera_index = self._pending_camera
                self._pending_camera = None
                reopen_needed = True

            if self._pending_res is not None:
                self.target_width, self.target_height = self._pending_res
                self._pending_res = None
                reopen_needed = True

            if reopen_needed:
                if cap is not None:
                    cap.release()
                cap = self._open_camera()

            if cap is not None and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    self.frame_ready.emit(frame)
                else:
                    self.msleep(15)
            else:
                self.msleep(100)

        if cap is not None:
            cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

class FloatingCamera(QWidget):
    def __init__(self, width=320, height=420, corner_radius=28, camera_index=0, initial_config=None):
        super().__init__()
        
        cfg = initial_config if initial_config is not None else load_config() or {}

        # Configuracion persistente restaurada
        self.corner_radius = cfg.get("corner_radius", corner_radius)
        self.is_circle = cfg.get("is_circle", False)
        self.mirror_mode = cfg.get("mirror_mode", True)
        self.camera_index = cfg.get("camera_index", camera_index)
        self.target_res = tuple(cfg.get("target_res", [1920, 1080]))
        self.actual_res = self.target_res
        self.sharpness_boost = cfg.get("sharpness_boost", True)

        # Zoom y Encuadre (Zona de la camara)
        self.zoom_factor = float(cfg.get("zoom_factor", 1.0))
        self.pan_offset_x = int(cfg.get("pan_offset_x", 0))
        self.pan_offset_y = int(cfg.get("pan_offset_y", 0))
        self.panning = False
        self.pan_start_mouse = QPoint()
        self.pan_start_offset = (0, 0)

        # Temporizador para guardado automatico debounced
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(300)
        self.save_timer.timeout.connect(self.save_config)

        # Estados de arrastre y redimensionado de ventana
        self.drag_position = QPoint()
        self.resize_mode = None      # 'corner', 'right', 'bottom'
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = None
        self.resize_margin = 16

        self.current_qimg = None

        self.setWindowTitle("Maicol Cam")
        icon_path = get_app_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Configuracion de ventana flotante sin bordes
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        # Restaurar tamano
        init_w = int(cfg.get("width", width))
        init_h = int(cfg.get("height", height))
        self.resize(init_w, init_h)

        # Restaurar o calcular posicion en pantalla
        self._setup_initial_position(cfg, init_w, init_h)

        # Iniciar captura de video en Full HD 1080p
        self.thread = VideoCaptureThread(
            camera_index=self.camera_index,
            target_width=self.target_res[0],
            target_height=self.target_res[1]
        )
        self.thread.frame_ready.connect(self.on_new_frame)
        self.thread.resolution_changed.connect(self.on_resolution_changed)
        self.thread.start()

    def _setup_initial_position(self, cfg, w, h):
        if "pos_x" in cfg and "pos_y" in cfg:
            saved_x = int(cfg["pos_x"])
            saved_y = int(cfg["pos_y"])
            intersects_screen = False
            for screen in QApplication.screens():
                geom = screen.geometry()
                if geom.intersects(QRectF(saved_x, saved_y, w, h).toRect()):
                    intersects_screen = True
                    break
            if intersects_screen:
                self.move(saved_x, saved_y)
                return

        screen = QApplication.primaryScreen().availableGeometry()
        pos_x = max(20, screen.right() - w - 40)
        pos_y = max(20, screen.bottom() - h - 60)
        self.move(pos_x, pos_y)

    def schedule_save(self):
        if hasattr(self, 'save_timer'):
            self.save_timer.start(300)

    def save_config(self):
        if hasattr(self, 'save_timer'):
            self.save_timer.stop()

        cfg = {
            "pos_x": int(self.x()),
            "pos_y": int(self.y()),
            "width": int(self.width()),
            "height": int(self.height()),
            "is_circle": bool(self.is_circle),
            "corner_radius": int(self.corner_radius),
            "mirror_mode": bool(self.mirror_mode),
            "camera_index": int(self.camera_index),
            "target_res": [int(self.target_res[0]), int(self.target_res[1])],
            "sharpness_boost": bool(self.sharpness_boost),
            "zoom_factor": float(round(self.zoom_factor, 2)),
            "pan_offset_x": int(self.pan_offset_x),
            "pan_offset_y": int(self.pan_offset_y),
        }
        try:
            cfg_path = get_config_path()
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.schedule_save()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.schedule_save()

    def on_resolution_changed(self, w, h):
        self.actual_res = (w, h)

    def on_new_frame(self, frame):
        h, w, ch = frame.shape

        win_w, win_h = max(60, self.width()), max(60, self.height())
        dpr = float(self.devicePixelRatio())
        phys_w = max(60, int(round(win_w * dpr)))
        phys_h = max(60, int(round(win_h * dpr)))

        target_aspect = win_w / win_h
        current_aspect = w / h

        # 1. Dimensiones base del lienzo de corte
        if current_aspect > target_aspect:
            base_h = h
            base_w = int(h * target_aspect)
        else:
            base_w = w
            base_h = int(w / target_aspect)

        # 2. Aplicar factor de zoom a la zona de la camara
        crop_w = max(20, min(w, int(base_w / self.zoom_factor)))
        crop_h = max(20, min(h, int(base_h / self.zoom_factor)))

        # 3. Posicion del encuadre (Pan)
        center_x = (w - crop_w) // 2
        center_y = (h - crop_h) // 2

        if self.mirror_mode:
            crop_x = int(np.clip(center_x + self.pan_offset_x, 0, w - crop_w))
            start_x = w - (crop_x + crop_w)
        else:
            start_x = int(np.clip(center_x + self.pan_offset_x, 0, w - crop_w))

        start_y = int(np.clip(center_y + self.pan_offset_y, 0, h - crop_h))

        # 4. Extraer zona
        cropped = frame[start_y:start_y + crop_h, start_x:start_x + crop_w]

        # 5. Escalar al tamano de renderizado fisico
        if phys_w <= crop_w and phys_h <= crop_h:
            interp = cv2.INTER_AREA
        else:
            interp = cv2.INTER_LINEAR

        resized = cv2.resize(cropped, (phys_w, phys_h), interpolation=interp)

        # 6. Realce de nitidez HD
        if self.sharpness_boost:
            blurred = cv2.GaussianBlur(resized, (0, 0), 1.5)
            resized = cv2.addWeighted(resized, 1.25, blurred, -0.25, 0)

        # 7. Volteo espejo
        if self.mirror_mode:
            resized = cv2.flip(resized, 1)

        # 8. QImage nativo con DPR asignado
        bytes_per_line = ch * phys_w
        qimg = QImage(resized.data, phys_w, phys_h, bytes_per_line, QImage.Format.Format_BGR888).copy()
        qimg.setDevicePixelRatio(dpr)
        self.current_qimg = qimg
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = float(self.width()), float(self.height())
        radius = float(min(w, h) / 2.0) if self.is_circle else float(self.corner_radius)

        path = QPainterPath()
        path.addRoundedRect(QRectF(0.0, 0.0, w, h), radius, radius)
        painter.setClipPath(path)

        if self.current_qimg is not None:
            painter.drawImage(0, 0, self.current_qimg)
        else:
            painter.fillPath(path, QColor(25, 27, 34, 240))
            painter.setPen(QColor(220, 220, 225))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(0, 0, int(w), int(h), Qt.AlignmentFlag.AlignCenter, "Conectando Maicol Cam...")

        painter.setClipping(False)
        painter.setPen(QColor(255, 255, 255, 60))
        painter.drawRoundedRect(QRectF(0.75, 0.75, w - 1.5, h - 1.5), radius, radius)

        if not self.is_circle:
            painter.setPen(QColor(255, 255, 255, 80))
            painter.drawLine(int(w - 12), int(h - 4), int(w - 4), int(h - 12))
            painter.drawLine(int(w - 7), int(h - 4), int(w - 4), int(h - 7))

        painter.end()

    def get_resize_zone(self, pos):
        w, h = self.width(), self.height()
        near_right = (w - pos.x() <= self.resize_margin)
        near_bottom = (h - pos.y() <= self.resize_margin)

        if near_right and near_bottom:
            return 'corner'
        elif near_right:
            return 'right'
        elif near_bottom:
            return 'bottom'
        return None

    def mousePressEvent(self, event):
        # Mover encuadre con clic central
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.pan_start_mouse = event.globalPosition().toPoint()
            self.pan_start_offset = (self.pan_offset_x, self.pan_offset_y)
            self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            zone = self.get_resize_zone(event.pos())
            if zone:
                self.resize_mode = zone
                self.resize_start_pos = event.globalPosition().toPoint()
                self.resize_start_geometry = self.geometry()
            else:
                self.resize_mode = None
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.globalPosition().toPoint() - self.pan_start_mouse
            dx = -delta.x() if self.mirror_mode else delta.x()
            dy = delta.y()
            self.pan_offset_x = self.pan_start_offset[0] + int(dx * 1.5)
            self.pan_offset_y = self.pan_start_offset[1] + int(dy * 1.5)
            self.schedule_save()
            event.accept()
            return

        if not (event.buttons() & Qt.MouseButton.LeftButton):
            zone = self.get_resize_zone(event.pos())
            if zone == 'corner':
                self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            elif zone == 'right':
                self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            elif zone == 'bottom':
                self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        if self.resize_mode and (event.buttons() & Qt.MouseButton.LeftButton):
            delta = event.globalPosition().toPoint() - self.resize_start_pos
            orig = self.resize_start_geometry

            if self.resize_mode == 'corner':
                aspect = orig.height() / orig.width()
                new_w = max(160, min(1400, orig.width() + delta.x()))
                new_h = int(new_w * aspect)
                self.resize(new_w, new_h)
            elif self.resize_mode == 'right':
                new_w = max(160, min(1600, orig.width() + delta.x()))
                self.resize(new_w, self.height())
            elif self.resize_mode == 'bottom':
                new_h = max(160, min(1400, orig.height() + delta.y()))
                self.resize(self.width(), new_h)
            event.accept()

        elif (event.buttons() & Qt.MouseButton.LeftButton) and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.panning = False
        self.resize_mode = None
        self.drag_position = QPoint()
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.save_config()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset_pan_zoom()
            event.accept()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.08 if delta > 0 else 0.92
        aspect = self.height() / self.width()
        new_w = max(160, min(1400, int(self.width() * factor)))
        new_h = int(new_w * aspect)
        self.resize(new_w, new_h)
        self.schedule_save()
        event.accept()

    def set_canvas_aspect(self, width, height, is_circle=False):
        self.is_circle = is_circle
        self.resize(width, height)
        self.update()
        self.save_config()

    def set_resolution(self, width, height):
        self.target_res = (width, height)
        self.thread.set_resolution(width, height)
        self.current_qimg = None
        self.update()
        self.save_config()

    def toggle_sharpness(self):
        self.sharpness_boost = not self.sharpness_boost
        self.save_config()

    def show_context_menu(self, global_pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1c23;
                color: #ffffff;
                border: 1px solid #373b4d;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 22px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #2563eb;
            }
            QMenu::separator {
                height: 1px;
                background: #2e3344;
                margin: 4px 0px;
            }
        """)

        # 1. Menu Resolucion HD
        res_label = f"📺 Resolucion HD ({self.actual_res[0]}x{self.actual_res[1]})"
        res_menu = menu.addMenu(res_label)

        action_1080 = res_menu.addAction("⭐ Full HD 1080p (1920x1080)" + ("  ✓" if self.target_res == (1920, 1080) else ""))
        action_1080.triggered.connect(lambda: self.set_resolution(1920, 1080))

        action_720 = res_menu.addAction("🔹 HD 720p (1280x720)" + ("  ✓" if self.target_res == (1280, 720) else ""))
        action_720.triggered.connect(lambda: self.set_resolution(1280, 720))

        action_480 = res_menu.addAction("🔸 SD 480p (640x480)" + ("  ✓" if self.target_res == (640, 480) else ""))
        action_480.triggered.connect(lambda: self.set_resolution(640, 480))

        # Realce de nitidez HD
        sharp_text = f"✨ Realce de nitidez HD: {'Activado ✓' if self.sharpness_boost else 'Desactivado'}"
        sharp_action = menu.addAction(sharp_text)
        sharp_action.triggered.connect(self.toggle_sharpness)

        menu.addSeparator()

        # 2. Menu Formato del Lienzo
        canvas_menu = menu.addMenu("🖼️ Formato del lienzo")
        canvas_menu.addAction("📱 Vertical 9:16 (Stories / Reels)", lambda: self.set_canvas_aspect(270, 480))
        canvas_menu.addAction("📱 Vertical 3:4 (Retrato clasico)", lambda: self.set_canvas_aspect(315, 420))
        canvas_menu.addAction("🖥️ Horizontal 16:9 (Webcam panoramica)", lambda: self.set_canvas_aspect(480, 270))
        canvas_menu.addAction("🖥️ Horizontal 4:3 (Estandar)", lambda: self.set_canvas_aspect(400, 300))
        canvas_menu.addAction("⏹️ Cuadrado 1:1", lambda: self.set_canvas_aspect(340, 340))
        canvas_menu.addAction("⭕ Circulo 1:1", lambda: self.set_canvas_aspect(340, 340, is_circle=True))

        # 3. Menu Zona de la Camara y Zoom
        zoom_menu = menu.addMenu(f"🔍 Zona de camara (Zoom: {self.zoom_factor:.1f}x)")
        zoom_menu.addAction("Zoom 1.0x (Normal)", lambda: self.set_zoom(1.0))
        zoom_menu.addAction("Zoom 1.25x", lambda: self.set_zoom(1.25))
        zoom_menu.addAction("Zoom 1.5x", lambda: self.set_zoom(1.5))
        zoom_menu.addAction("Zoom 2.0x", lambda: self.set_zoom(2.0))
        zoom_menu.addAction("Zoom 3.0x", lambda: self.set_zoom(3.0))
        zoom_menu.addSeparator()
        zoom_menu.addAction("➕ Acercar zoom", lambda: self.set_zoom(min(4.0, self.zoom_factor + 0.25)))
        zoom_menu.addAction("➖ Alejar zoom", lambda: self.set_zoom(max(1.0, self.zoom_factor - 0.25)))
        zoom_menu.addSeparator()
        zoom_menu.addAction("🎯 Centrar encuadre y resetear", self.reset_pan_zoom)

        # 4. Menu Redondeo de esquinas
        corners_menu = menu.addMenu("⭕ Redondeo de esquinas")
        corners_menu.addAction("Circulo completo", lambda: self.set_rounding_mode(circle=True))
        corners_menu.addAction("Esquinas muy redondeadas (40px)", lambda: self.set_rounding_mode(radius=40))
        corners_menu.addAction("Esquinas normales (28px)", lambda: self.set_rounding_mode(radius=28))
        corners_menu.addAction("Esquinas suaves (14px)", lambda: self.set_rounding_mode(radius=14))
        corners_menu.addAction("Sin redondeo / Bordes rectos", lambda: self.set_rounding_mode(radius=0))

        menu.addSeparator()

        cam_action = menu.addAction(f"📷 Cambiar camara (Actual: {self.camera_index})")
        cam_action.triggered.connect(self.toggle_camera)

        mirror_action = menu.addAction(f"🔄 Modo espejo: {'Activado ✓' if self.mirror_mode else 'Desactivado'}")
        mirror_action.triggered.connect(self.toggle_mirror)

        menu.addSeparator()
        close_action = menu.addAction("❌ Cerrar Maicol Cam")
        close_action.triggered.connect(self.close)

        menu.exec(global_pos)

    def set_zoom(self, zoom):
        self.zoom_factor = zoom
        self.save_config()

    def reset_pan_zoom(self):
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.save_config()

    def set_rounding_mode(self, radius=28, circle=False):
        self.is_circle = circle
        self.corner_radius = radius
        self.update()
        self.save_config()

    def toggle_camera(self):
        self.camera_index = 1 if self.camera_index == 0 else 0
        self.thread.set_camera(self.camera_index)
        self.current_qimg = None
        self.update()
        self.save_config()

    def toggle_mirror(self):
        self.mirror_mode = not self.mirror_mode
        self.save_config()

    def closeEvent(self, event):
        self.save_config()
        self.thread.stop()
        event.accept()

def get_best_camera_index():
    for idx in [0, 1]:
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None and frame.mean() > 5:
                return idx
    return 0

if __name__ == "__main__":
    import ctypes
    try:
        myappid = 'santiagojorda.maicolcam.app.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    
    icon_path = get_app_icon_path()
    if icon_path and os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    cfg = load_config()
    if cfg is not None and "camera_index" in cfg:
        best_cam = cfg["camera_index"]
    else:
        best_cam = get_best_camera_index()
    window = FloatingCamera(camera_index=best_cam, initial_config=cfg)
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec())
