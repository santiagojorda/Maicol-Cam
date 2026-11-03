# maicol-cam

Una ventana flotante de camara web simple, ligera y sin bordes.

La idea de este proyecto es tener tu camara en pantalla sin ventanas pesadas, sin barras de titulo ni marcos molestos: solo tu video flotando limpiamente sobre tus aplicaciones, siempre visible mientras trabajas, grabas la pantalla o estas en llamada.

---

## Descarga directa (Windows)

Si solo queres usar la aplicacion sin instalar nada:

👉 **[Descargar MaicolCam.exe](https://github.com/santiagojorda/maicol-cam/releases/latest/download/MaicolCam.exe)**

*No requiere Python ni dependencias adicionales. Descargar y abrir.*

---

## Como usarla

### 1. Clonar el repositorio
```bash
git clone https://github.com/santiagojorda/maicol-cam.git
cd maicol-cam
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar
```bash
python webcam_float.py
```

Tambien podes hacer doble clic en `run.bat` para abrirla directamente sin consola negra.

---

## Compilar a .exe (Opcional)

Si queres compilar tu propio ejecutable:

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --noconsole --icon="webcam.ico" --name "MaicolCam" webcam_float.py
```
