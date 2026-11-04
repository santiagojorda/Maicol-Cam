# Maicol Cam

<p align="center">
  <img src="assets/logo_glace_rendered.png" width="160" alt="Maicol Cam Logo" />
</p>

Ventana flotante de camara web simple, ligera y sin bordes.

La idea del proyecto es tener la camara en pantalla sin ventanas pesadas, sin barras de titulo ni marcos molestos: video flotando limpiamente sobre el resto de las aplicaciones, siempre visible durante grabaciones de pantalla, llamadas o transmisiones.

---

## Descarga directa (Windows)

Para usar la aplicacion directamente sin instalar dependencias:

👉 **[Descargar MaicolCam.exe](https://github.com/santiagojorda/Maicol-Cam/releases/latest/download/MaicolCam.exe)**

*No requiere Python ni dependencias adicionales. Descargar y abrir.*

---

## Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/santiagojorda/Maicol-Cam.git
cd Maicol-Cam
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar
```bash
python webcam_float.py
```

Tambien se puede ejecutar `run.bat` para iniciar directamente sin consola.

---

## Compilar a .exe (Opcional)

Para compilar el ejecutable:

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --noconsole --icon="webcam.ico" --name "MaicolCam" webcam_float.py
```
