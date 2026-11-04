<p align="center">
  <img src="assets/logo_glace_rendered.png" width="140" alt="Maicol Cam Logo" />
</p>

<h1 align="center">Maicol Cam</h1>

<p align="center">
  Ventana flotante de camara web simple, ligera y sin bordes para Windows.
</p>

<p align="center">
  <a href="https://github.com/santiagojorda/Maicol-Cam/actions/workflows/build-and-test.yml">
    <img src="https://github.com/santiagojorda/Maicol-Cam/actions/workflows/build-and-test.yml/badge.svg" alt="Build and Test" />
  </a>
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
</p>

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

## Tests

Para ejecutar las pruebas automatizadas del proyecto:

```bash
pip install pytest
pytest
```

---

## Compilar a .exe (Opcional)

Para compilar el ejecutable:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon assets/maicol_cam.ico --add-data "assets;assets" webcam_float.py --name "MaicolCam"
```
```
