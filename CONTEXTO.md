# TP2 Reconstrucción 3D: contexto de trabajo

Estado al 16/10/2026 (último commit `ad88081`). Resume lo hecho, los resultados y lo que
falta, para que cualquiera del grupo pueda seguir desde acá en otra computadora.

Repo: https://github.com/FrancoSandri/tp2_reconstruccion_3d (rama `main`).

## 1. Estado del pipeline

| Etapa del TP | Estado | Dónde |
|---|---|---|
| 4.1 Calibración y rectificación | **Hecha** con la tool `calib-stereo` a 1280x720. Falta reportar el RMS en el notebook (ver 4.1) | `calibration/`, notebook "Carga de la calibración" y "Rectificación" |
| 4.2.1 Disparidad | **Hecha** con SGBM; parámetros ajustados y comparados en `stereodemo` | notebook "Disparidad con SGBM", `imgs/` |
| 4.2.2 Nube local | **Hecha** con `reprojectImageTo3D(disp, Q)` | notebook "Nube de puntos local" |
| 4.2.3 Pose global | **Hecha** con ChArUco + `solvePnP` (IPPE + refinamiento LM) | notebook "Tablero ChArUco" y "Pose global" |
| 4.2.4 Paso al marco global | **Hecha** (incluye el paso por `R1`) | notebook "Pose global" |
| 4.3 Fusión y optimización | **Hecha** en Open3D; `.ply` binario exportado | notebook "Fusión", `outputs/stitch_final.ply` |
| 5 Medición métrica | **Hecha**; falta la medida real para el error relativo | notebook "Medición métrica" |
| Informe | **Sin empezar** | |

## 2. Estructura del repo

- `notebooks/tp2.ipynb`: pipeline completo, con el estilo del TP1 (títulos centrados, una
  explicación corta por etapa, prints simples). Corre de punta a punta en unos minutos.
- `notebooks/utils.py`: funciones auxiliares (lectura de imágenes, detección ChArUco, pose,
  disparidad, nube local, gráficos). El notebook las importa con `from utils import ...`,
  así que hay que abrirlo **desde la carpeta `notebooks/`**.
- `calibration/`: `stereo_calibration.pkl` y `stereo_maps.pkl` de la tool.
- `datasets/stereo_stitch_charuco/captures/`: 27 pares crudos del peluche de Stitch sobre el
  ChArUco (1280x720). `rect/` tiene los pares rectificados en PNG y el json de `stereodemo`.
- `datasets/calib/`: 30 pares del checkerboard con los que se calibró (1280x720), subidos por Alan.
- `datasets/stereo_budha_board/`, `datasets/stereo_stitch_charuco/calib/`: material de la
  cátedra (Buda, 1080p). No se usa.
- `imgs/`: capturas de `stereodemo` (par 13: SGBM bloque 5, SGBM bloque 9, CREStereo),
  `tiempos_disparidad.txt` y `meshlab/` (frente, costado y atrás de la nube final).
- `outputs/stitch_final.ply`: nube final (4,9 MB, ~183 000 puntos, binario). Es el entregable.
- `code_examples/`: ejemplos de la cátedra (charuco y disparidad). No se tocan.
- `src/stereo_matching.py`: vacío, se puede borrar.

## 3. Datos clave

**Cámara y calibración** (ELP de la cátedra, modo 2560x720):
- fx ≈ 403 px, cx ≈ 636, cy ≈ 356; baseline |T| = **60,17 mm**.
- Tras rectificar: f = 405,9 px, centro (631,0, 352,4). z = f·B/d ≈ 24 422 / d (mm, px).

**Checkerboard de calibración** (`datasets/calib/`): 10x7 casilleros, o sea **9x6 esquinas
internas**. Casillero ≈ **28 mm**, inferido comparando con el baseline del pkl (confirmar con regla).

**ChArUco de las capturas**: `DICT_5X5_100`, 9x13 casilleros, casillero 42,0 mm, marcador
31,5 mm (está impreso en el borde del tablero). 96 esquinas internas.

**SGBM**: `minDisparity=8, numDisparities=144, blockSize=5, P1=600, P2=2400 (8·3·5², 32·3·5²),
uniquenessRatio=10, speckleWindowSize=200, speckleRange=2, disp12MaxDiff=1, preFilterCap=63,
mode=SGBM_3WAY`. Se corre en color; en `stereodemo` (que pasa a gris) el equivalente es
`Num Disparities=160, P1=200, P2=800` con el resto igual. Diferencia mediana entre ambos: 0,06 px.

## 4. Resultados (para el informe)

### 4.1 Calibración
- RMS estéreo recalculado con las fotos de `datasets/calib/` (script aparte, `stereoCalibrate`
  con flags=0, 29 de 30 pares; en el par 7 no se detecta el tablero en la izquierda):
  **1,27 px**. Monocular: izquierda 0,70 px, derecha 0,45 px. Reproduce los intrínsecos del pkl
  (fx 403,26 vs 403,15). Alan está agregando esta sección al notebook.
- Verificación independiente con el ChArUco (en el notebook): RMS izquierda (PnP) 0,495 px,
  derecha vía `R, T` 1,344 px; lado del casillero triangulado 42,12 mm (real 42,0, error 0,3 %).
- `dy` residual tras rectificar: 0,2 a 1,8 px, siempre del mismo signo (sistemático), mayor en
  los pares 0 a 7.

### 4.2 Disparidad (par 13, en `stereodemo`)
| Método | Tiempo | Observación |
|---|---|---|
| SGBM bloque 5 | 173 ms | detalle en bordes, huecos chicos (ojo brillante, oclusiones) |
| SGBM bloque 9 | 143 ms | más suave, bordes engordados (la diferencia de tiempo es ruido) |
| CREStereo 640x480, 5 iter. | 4882 ms | denso y sin huecos, pero ~30x más lento e inventa en zonas sin textura |

Se eligió SGBM bloque 5: los huecos se compensan con las 25 vistas. Disparidad válida en
el notebook: 48 % (par 0), 57 % (par 13), 66 % (par 25).

### 4.3 Nube local, pose y fusión
- Chequeo de fórmula: `reprojectImageTo3D` coincide exactamente con f·B/d.
- Pose: 25 de 27 pares aceptados (el 20 tiene RMS PnP 16 px y el 25 no detecta el tablero).
  Pares dudosos que entraron: 1 (10 esquinas) y 19 (RMS 1,56 px).
- Puntos por etapa: 9 500 201 → caja 1 602 460 → voxel 2 mm 250 180 → outliers 243 778 →
  sin plano del tablero ~186 000 → cluster principal **~183 000** (varía ±1 % por RANSAC).

### 4.4 Medición
- **Alto 279,9 mm** (p99,5 de la distancia al plano del tablero ajustado; máximo 285,8 mm).
- **Ancho 295,4 mm** (de oreja a oreja, `minAreaRect` sobre el plano), **profundidad 172,7 mm**.
- El tablero reconstruido por estéreo queda ~7 mm por encima de z = 0 del PnP (sesgo sistemático
  de ~1,5 % de la distancia, punto para la discusión). Medir respecto al plano ajustado lo cancela.

## 5. Pendientes

1. **Medida real del peluche** (alto desde la base a la punta de la cabeza, ancho de punta a punta
   de las orejas): cargar `REAL_ALTO_MM` y `REAL_ANCHO_MM` en la celda de medición.
2. **RMS de la calibración en el notebook** (Alan) y `datasets/calib/checkerboard.txt` con el
   tablero (9x6 esquinas, casillero en mm).
3. **Entregables del repo**: `README.md` (qué es, estructura, instalación, cómo correr),
   `requirements.txt` con versiones y `.gitignore` (`.venv/`, `__pycache__/`, `desktop.ini`).
4. **Informe** (8 páginas máximo): Introducción y Marco teórico, Metodología, Resultados y
   Discusión. Las preguntas a responder están en las páginas 7 y 8 del enunciado.
5. **Entrega**: `.ply` en un link de descarga directa (Drive) y el dataset propio en otro link.
6. Opcionales: probar sin los pares 1 y 19 (robustez), ICP, mallado con Poisson.

Puntos para la discusión: `dy` sistemático de la rectificación, sesgo de ~7 mm entre estéreo y
PnP, huecos por oclusión y por el ojo brillante, flying pixels grises en el borde de las orejas,
SGBM contra CREStereo, pares con pose dudosa.

## 6. Entorno

Se trabaja en **WSL (Ubuntu 22.04)** con el Python de **miniconda** (3.13):
`source /root/miniconda3/bin/activate`. Tiene OpenCV 4.13 + contrib, Open3D 0.20, stereodemo,
onnxruntime, torch, i308-utils y jupyter.

- **No usar el Python del sistema de Ubuntu** (3.11.0rc1): torch falla con
  `sys.get_int_max_str_digits`.
- `stereodemo` necesita Vulkan para abrir la ventana: `apt install -y libvulkan1 mesa-vulkan-drivers`.
- Si Open3D tira `GLIBCXX_3.4.30 not found`: `conda install -c conda-forge "libstdcxx-ng>=12" "libgcc-ng>=12"`.
- OpenCV 4.12 rompe el módulo ArUco: usar 4.11 o 4.13.
- MeshLab está instalado en Windows (para mirar el `.ply`: apagar Shading y fondo blanco).

Para correr el notebook: activar conda, `cd repo/notebooks`, `jupyter lab`. Para ajustar
disparidad: desde `repo/`, `stereodemo datasets/stereo_stitch_charuco/rect`.

## 7. Detalles al commitear

- Correr el notebook reescribe `datasets/stereo_stitch_charuco/rect/stereodemo_calibration.json`
  solo con cambios de saltos de línea: descartarlo con
  `git checkout -- datasets/stereo_stitch_charuco/rect/stereodemo_calibration.json`.
- No subir `.venv/`, `notebooks/__pycache__/` ni los `desktop.ini` de OneDrive: agregar archivos
  de a uno (no `git add .`) hasta que exista el `.gitignore`.
- Hacer `git pull` antes de tocar el notebook: los `.ipynb` no se mezclan bien si dos personas
  los editan a la vez.
