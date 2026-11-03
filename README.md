# 📷 Cámara Flotante Minimalista

Una ventana flotante de cámara web **simple, ligera y sin bordes**. 

La idea principal de este proyecto es tener tu cámara en pantalla **sin ventanas pesadas, sin barras de título ni marcos molestos**: solo tu video flotando limpiamente sobre tus aplicaciones, siempre visible mientras trabajas, grabas la pantalla o estás en llamada.

---

## 📥 Descarga directa (Windows)

Si solo quieres usar la aplicación sin instalar nada:

👉 **[Descargar CamaraFlotante.exe v1.0.0](https://github.com/santiagojorda/camara-flotante/releases/download/v1.0.0/CamaraFlotante.exe)** *(87 MB)*

*Auto-contenido: no requiere Python, Git ni dependencias adicionales. Descargar y abrir.*

---

## ✨ Características

- 🪟 **Diseño 100% minimalista:** sin bordes, sin barras de ventana y con esquinas redondeadas o modo circular.
- 📌 **Siempre visible (Always on Top):** se mantiene por encima de cualquier programa o juego.
- 🌟 **Calidad Full HD (1080p):** aprovecha el sensor de tu webcam a máxima resolución y con soporte para pantallas de alta densidad (High-DPI).
- ✨ **Filtro de nitidez HD:** realce sutil de bordes para una imagen más nítida y limpia.
- 📐 **Lienzo adaptable:** formatos predefinidos (Vertical 9:16 para Reels/TikTok, 3:4, Horizontal 16:9, Cuadrado 1:1 o Círculo).
- 🔍 **Zoom y Encuadre digital:** haz zoom y reubica tu encuadre fácilmente sin mover la webcam física.
- 💾 **Persistencia automática:** recuerda tu tamaño, posición en pantalla, zoom, cámara y ajustes entre cierres de forma 100% automática.

---

## 🚀 Cómo usarla

### 1. Clonar el repositorio
```bash
git clone https://github.com/santiagojorda/camara-flotante.git
cd camara-flotante
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar
```bash
python webcam_float.py
```

> **Tip:** También puedes ejecutarlo con `pythonw webcam_float.py` si no quieres que se abra ninguna ventana de consola negra.

---

## 🎮 Controles rápidos

### 🖱️ Con el mouse

| Acción | Control |
| :--- | :--- |
| **Mover la ventana** | Arrastrar con clic izquierdo desde el centro |
| **Cambiar tamaño libre** | Arrastrar los bordes derecho, inferior o esquina |
| **Cambiar tamaño proporcional** | Rueda del mouse (Scroll) |
| **Hacer Zoom** | <kbd>Ctrl</kbd> + Rueda del mouse |
| **Mover el encuadre (Pan)** | Clic con la rueda central **o** <kbd>Ctrl</kbd> + Clic izquierdo y arrastrar |
| **Restaurar zoom y encuadre** | Doble clic izquierdo |
| **Menú de opciones completo** | Clic derecho |

### ⌨️ Con el teclado

| Tecla | Acción |
| :--- | :--- |
| <kbd>M</kbd> | Alternar modo espejo (invertir horizontalmente) |
| <kbd>C</kbd> | Cambiar de cámara (0 / 1) |
| <kbd>S</kbd> | Activar / Desactivar realce de nitidez HD |
| <kbd>H</kbd> | Alternar entre 1080p y 720p |
| <kbd>+</kbd> / <kbd>-</kbd> | Zoom in / Zoom out |
| <kbd>Flechas</kbd> | Mover el encuadre (arriba, abajo, izquierda, derecha) |
| <kbd>0</kbd> | Resetear zoom y encuadre al centro |
| <kbd>Esc</kbd> | Cerrar la aplicación |

---

## 📦 Compilar a ejecutable `.exe` (Opcional)

Si quieres tener un archivo `.exe` independiente que puedas abrir directamente sin instalar Python:

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --noconsole --icon="webcam.ico" --name "CamaraFlotante" webcam_float.py
```

El ejecutable quedará generado dentro de la carpeta `dist/`.

---

## 🛠️ Tecnologías utilizadas

- **Python 3.12+**
- **PyQt6** (interfaz gráfica flotante y eventos)
- **OpenCV (cv2)** (captura de video DirectShow en 1080p y transformaciones)
- **NumPy**
