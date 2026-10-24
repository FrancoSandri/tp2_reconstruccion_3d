# TP2 Reconstrucción 3D: contexto de trabajo

Estado al 23/10/2026 (último commit `d25efcb`; números de la corrida de Franco, `85b7b44`). Resume lo hecho, los resultados y lo que
falta, para que cualquiera del grupo pueda seguir desde acá en otra computadora. Lo último que se hizo está en la sección 0.

Repo: https://github.com/FrancoSandri/tp2_reconstruccion_3d (rama `main`).

## 0. Últimos cambios (en qué estamos trabajando)

- **23/10, Alan** (`1c56173`): notebook opcional `notebooks/opcional.ipynb` con normales y malla de
  Poisson, y `plot_mesh` en `utils.py`. Ajustes chicos en el informe (rango de disparidad 40–110 px y
  explicación de por qué el alto y el ancho dan menos que la regla) y en `tp2.ipynb` (comentarios).
- **23/10, Luis** (`d25efcb`): notebook opcional ejecutado y guardado con salidas, malla en
  `outputs/stitch_poisson.ply`, y el informe con la malla de Poisson: subsección en Metodología y en
  Resultados, figura 10, referencias de Poisson y Taubin, conclusión actualizada. Para que las
  figuras no quedaran después de las referencias se pasaron optimización, MeshLab y Poisson a una
  columna; el informe quedó en **6 páginas**. Ya está subido a Overleaf.
- **22/10, Franco**: links de entrega en Drive y README.
- **21/10, Luis**: README, `requirements.txt` y `.gitignore`.
- **20/10, Luis**: informe actualizado a la corrida de Franco y capturas de MeshLab sobre el `.ply` nuevo.

Antes de tocar algo: `git pull`, y si se cambia el informe en Overleaf, copiar el `.tex` al repo (y al revés).

## 1. Estado del pipeline

| Etapa del TP | Estado | Dónde |
|---|---|---|
| 4.1 Calibración y rectificación | **Hecha** con la tool `calib-stereo` a 1280x720; RMS 1,25 px recalculado en el notebook | `calibration/`, `datasets/calib/`, notebook "Carga de la calibración", "Error de reproyección de la calibración" y "Rectificación" |
| 4.2.1 Disparidad | **Hecha** con SGBM; parámetros ajustados y comparados en `stereodemo` | notebook "Disparidad con SGBM", `imgs/` |
| 4.2.2 Nube local | **Hecha** con `reprojectImageTo3D(disp, Q)` | notebook "Nube de puntos local" |
| 4.2.3 Pose global | **Hecha** con ChArUco + `solvePnP` (IPPE + refinamiento LM) | notebook "Tablero ChArUco" y "Pose global" |
| 4.2.4 Paso al marco global | **Hecha** (incluye el paso por `R1`) | notebook "Pose global" |
| 4.3 Fusión y optimización | **Hecha** en Open3D; `.ply` binario exportado | notebook "Fusión", `outputs/stitch_final.ply` |
| 5 Medición métrica | **Hecha**, con error relativo contra la medida real | notebook "Medición métrica" |
| Opcional: normales y mallado con Poisson | **Hecho** (malla de 74 102 vértices, a 1 mm de la nube) | `notebooks/opcional.ipynb`, `outputs/stitch_poisson.ply` |
| Informe | **Final** (LaTeX, 6 páginas, incluye Poisson; igual al de Overleaf al 23/10) | `informe/` |
| README, requirements, .gitignore | **Hechos** | raíz del repo |
| Links de entrega (Drive) | **Hechos**: `.ply` y zip del dataset, públicos con el link | README, sección Entregables |

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
- `notebooks/opcional.ipynb`: paso opcional, parte de `stitch_final.ply` sin modificarlo: normales, malla de
  Poisson, figura `informe/img/poisson.png` y `outputs/stitch_poisson.ply`. Se abre igual que `tp2.ipynb`.
- `outputs/stitch_final.ply`: nube final (4,7 MB, 175 791 puntos, binario). Es el entregable.
- `outputs/stitch_poisson.ply`: malla de Poisson (5,7 MB, 74 102 vértices, 149 999 triángulos, binario).
- `informe/`: `embon_sandri_yeger-tp2-informe.tex` y sus figuras en `img/` (se compila en Overleaf con pdfLaTeX).
  La versión del repo es la final (igual a la de Overleaf al 23/10). Si se vuelve a tocar en
  Overleaf, copiar el `.tex` al repo.
  En la carpeta de OneDrive de Luis, `../informe_tp2_overleaf.zip` y `../informe_tp2_preview.pdf`
  son del 23/10 (al día); la carpeta `../informe_tp2_overleaf/` es vieja.
- `code_examples/`: ejemplos de la cátedra (charuco y disparidad). No se tocan.
- `README.md` y `requirements.txt` (versiones del entorno conda de WSL).

## 3. Datos clave

**Cámara y calibración** (ELP de la cátedra, modo 2560x720):
- fx ≈ 403 px, cx ≈ 636, cy ≈ 356; baseline |T| = **60,17 mm**.
- Tras rectificar: f = 405,9 px, centro (631,0, 352,4). z = f·B/d ≈ 24 422 / d (mm, px).

**Checkerboard de calibración** (`datasets/calib/`): 10x7 casilleros, o sea **9x6 esquinas
internas**. Casillero de **28 mm**: recalibrando con ese valor el baseline da 60,18 mm contra 60,17 del pkl.

**ChArUco de las capturas**: `DICT_5X5_100`, 9x13 casilleros, casillero 42,0 mm, marcador
31,5 mm (está impreso en el borde del tablero). 96 esquinas internas.

**SGBM**: `minDisparity=8, numDisparities=144, blockSize=5, P1=600, P2=2400 (8·3·5², 32·3·5²),
uniquenessRatio=10, speckleWindowSize=200, speckleRange=2, disp12MaxDiff=1, preFilterCap=63,
mode=SGBM_3WAY`. Se corre en color; en `stereodemo` (que pasa a gris) el equivalente es
`Num Disparities=160, P1=200, P2=800` con el resto igual. Diferencia mediana entre ambos: 0,06 px.

## 4. Resultados (para el informe)

Corrida de `85b7b44` (Franco). Con otra versión de OpenCV algunos números cambiaron respecto de
corridas anteriores (por ejemplo el par 1 deja de detectarse); el informe usa estos.

### 4.1 Calibración
- **RMS estéreo 1,25 px** (1,248; sección "Error de reproyección de la calibración" del notebook):
  `stereoCalibrate` con flags=0 sobre las fotos de `datasets/calib/`, 29 de 30 pares (en el par 7
  `findChessboardCorners` no detecta el tablero en la imagen izquierda, probablemente por un
  reflejo). Reproduce el pkl: fx 402,05 vs 403,15 px (izq.), 400,82 vs 401,72 px (der.),
  baseline 60,18 vs 60,17 mm. Referencia: la calibración de la cátedra daba 1,055 px.
  Monocular (calculado aparte, no está en el notebook): izquierda 0,70 px, derecha 0,45 px.
- Verificación independiente con el ChArUco (en el notebook): RMS izquierda (PnP) 0,478 px,
  derecha vía `R, T` 1,310 px; lado del casillero triangulado 42,13 mm de mediana (media
  42,11 ± 1,32; real 42,0, error 0,3 %).
- `dy` residual tras rectificar: 0,2 a 1,5 px, siempre del mismo signo (sistemático), mayor en
  los pares 0 a 7.

### 4.2 Disparidad (par 13, en `stereodemo`)
| Método | Tiempo | Observación |
|---|---|---|
| SGBM bloque 5 | 173 ms | detalle en bordes, huecos chicos (ojo brillante, oclusiones) |
| SGBM bloque 9 | 143 ms | más suave, bordes engordados (la diferencia de tiempo es ruido) |
| CREStereo 640x480, 5 iter. | 4882 ms | denso y sin huecos, pero ~30x más lento e inventa en zonas sin textura |

Se eligió SGBM bloque 5: los huecos se compensan con las otras vistas. Disparidad válida en
el notebook: 48 a 64 % según el par (43 % de los píxeles con punto 3D en el par 13).

### 4.3 Nube local, pose y fusión
- Chequeo de fórmula: `reprojectImageTo3D` coincide exactamente con f·B/d (d = 55 px → z = 444,0 mm).
- Pose: **24 de 27 pares aceptados** (1 y 25 no detectan el tablero, el 20 tiene RMS PnP 6,06 px).
  RMS PnP de los aceptados entre 0,23 y 1,80 px. Par dudoso que entró: 19 (RMS 1,80 px, 26 de 38
  esquinas). El par 1 está en el límite: con otra versión de OpenCV entra con 10 esquinas y el
  alto cambia solo 0,2 mm (279,9 vs 279,7).
- Puntos por etapa: 9 282 487 → caja 1 510 554 → voxel 2 mm 239 309 → outliers 233 096 →
  sin plano del tablero 180 711 → cluster principal **175 791** (varía ±1 % por RANSAC).

### 4.4 Medición
| | Estimado | Real (regla) | Error |
|---|---|---|---|
| Alto (p99,5 de la distancia al plano ajustado; máx. 286,0) | 279,7 mm | 290 mm | −3,5 % |
| Ancho (orejas, `minAreaRect` sobre el plano) | 294,0 mm | 300 mm | −2,0 % |
| Profundidad | 172,5 mm | 170 mm | +1,4 % |

- El tablero reconstruido por estéreo queda 10,4 mm por encima de z = 0 del PnP (sesgo sistemático
  de ~2 % de la distancia, está en la discusión). Medir respecto al plano ajustado lo cancela.

### 4.5 Malla de Poisson (opcional, `notebooks/opcional.ipynb`)
- Normales con `estimate_normals` (radio 10 mm, 50 vecinos) y orientación consistente
  (`orient_normals_consistent_tangent_plane`); el 76 % apunta hacia afuera del centroide (no es
  100 % porque el peluche no es convexo).
- Poisson `depth=8` (celdas de ~1,5 mm): 253 216 vértices → recorte por densidad (5 % menos sostenido)
  240 555 → recorte con la caja 240 544 → Taubin (10 iteraciones) → decimación a **74 102 vértices
  y 149 999 triángulos**.
- Fidelidad: distancia vértice-nube de mediana 1,00 mm, percentil 95 1,96 mm, máximo 4,96 mm.
- No es cerrada (base y hueco entre brazo y cuerpo abiertos a propósito). La medición se hace sobre
  la nube, no sobre la malla.

## 5. Pendientes

No queda nada obligatorio. Opcional que no se hizo: ICP.

Detalles chicos que se pueden hacer:
- El README no menciona `notebooks/opcional.ipynb` ni `outputs/stitch_poisson.ply` (estructura y entregables).
- Confirmar con Franco la versión de OpenCV de su corrida: el informe dice OpenCV 4.13.

Entrega en Drive (hecho el 22/10), carpeta
[Dataset-tp2-reconstruccion-3d](https://drive.google.com/drive/folders/1YVeUoTn8iDGOQCYMBNBdYpeawiBg1VgT?usp=sharing),
con acceso de lector para cualquiera con el link:
- `stitch_final.ply` (4,7 MB): id `1Ybi883HTbzfYiLK3ib5xr77Oo-P2mrJS`.
- `dataset_stitch_tp2.zip` (22,8 MB, sin compresión): `datasets/calib/` y
  `datasets/stereo_stitch_charuco/captures/` con sus rutas. No incluye `rect/` (61 MB, lo genera
  el notebook). Id `1MptTQNZ2Sqe5Pskws_koW8t22n-sc9yt`.
Si se regenera el `.ply`, hay que volver a subirlo (reemplazar la versión en Drive mantiene el id).

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

Para correr el notebook: activar conda y abrir `repo/notebooks/tp2.ipynb` en VS Code con ese kernel
(el conda no tiene `jupyterlab` instalado). Para ajustar
disparidad: desde `repo/`, `stereodemo datasets/stereo_stitch_charuco/rect`.

## 7. Detalles al commitear

- Correr el notebook reescribe `datasets/stereo_stitch_charuco/rect/stereodemo_calibration.json`
  solo con cambios de saltos de línea: descartarlo con
  `git checkout -- datasets/stereo_stitch_charuco/rect/stereodemo_calibration.json`.
- `.venv/`, `__pycache__/` y los `desktop.ini` de OneDrive ya están en el `.gitignore`.
- Hacer `git pull` antes de tocar el notebook: los `.ipynb` no se mezclan bien si dos personas
  los editan a la vez.
