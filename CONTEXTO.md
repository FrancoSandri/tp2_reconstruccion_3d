# TP2 Reconstrucción 3D: contexto de trabajo

Estado al 10/10/2026. Resume lo hecho hasta ahora, lo que se descubrió del dataset
y lo que falta, para que cualquiera del grupo pueda seguir desde acá.

## 1. Dónde estamos en el pipeline del enunciado

| Etapa del TP | Estado | Material de referencia |
|---|---|---|
| 4.1 Calibración y rectificación | **Hecha.** Calibración propia con la tool `calib-stereo`; pares rectificados generados. | Tutorial 6, celdas 8 a 56; `calib-tool.md` |
| 4.2.1 Stereo matching (disparidad) | Siguiente paso. Pares listos para la tool `stereodemo`. | Tutorial 6, celdas 57 a 68; `code_examples/stereodemo_disp_example/` |
| 4.2.2 Nube local con `Q` + `reprojectImageTo3D` | Pendiente | Tutorial 6, celdas 69 a 83 (versión simplificada) |
| 4.2.3 Pose global con ChArUco + `solvePnP` | Pendiente. Falta identificar el tablero (ver sección 4). | Tutorial 7, celdas 24 a 36; `code_examples/charuco_example/` |
| 4.2.4 Transformación al marco global | Pendiente | Tutorial 7, celda 57 |
| 4.3 Fusión y optimización en Open3D | Pendiente | Tutorial 7, celdas 64 a 69 |
| 5 Medición métrica | Pendiente | |

## 2. El dataset propio

Está en `datasets/stereo_stitch_charuco/` (antes `stereo_budha_charuco`, renombrada; el
commit viejo todavía la tiene bajo ese nombre) y **no es el de la cátedra**:

- `captures/`: 27 pares (`left_N.jpg` / `right_N.jpg`, N = 0..26) de un peluche de
  Stitch sobre un tablero ChArUco, tomados en el aula con la cámara ELP de la cátedra.
  Resolución **1280x720** (modo 2560x720 de la cámara). Son capturas **crudas**, sin
  rectificar: lo verificamos midiendo que puntos correspondientes difieren ~4 px en
  vertical antes de rectificar y menos de 1 px después.
- `calib/`: son las imágenes de calibración **de la cátedra**, a 1920x1080. No se
  usaron porque están en otra resolución (y posiblemente otra unidad de cámara).
- No hay `markers.yaml` para las capturas propias: hay que crearlo cuando sepamos la
  geometría del tablero (sección 4).

`datasets/stereo_budha_board/` es el dataset original de la cátedra, intacto.

## 3. Calibración (etapa 4.1)

La calibración válida es la que hizo el grupo con la tool a 1280x720. Los archivos
están en la raíz del repo (`stereo_calibration.pkl`, `stereo_maps.pkl`):

- `stereo_calibration.pkl`: claves `left_K, left_dist, right_K, right_dist, R, T, E, F,
  image_size`. Valores principales: fx ≈ 403 px, cx ≈ 636, cy ≈ 356 (izq) / 349 (der),
  baseline |T| = **60,17 mm**, `image_size = (1280, 720)`. El RMS de reproyección no
  quedó guardado en el pkl: **hay que recuperarlo de la consola de la tool o recalcularlo**,
  porque el informe lo pide.
- `stereo_maps.pkl`: `left_map_x/y, right_map_x/y, R1, R2, P1, P2, Q, validRoi1/2`.
  Tras rectificar la focal común es 405,9 px y el centro (631,0, 352,4). `Q` es la que
  va a `cv.reprojectImageTo3D` en 4.2.2.

Archivos auxiliares que **no se usan** pero quedan de referencia:
`stereo_calibration_1080p.pkl` (calibración hecha con las imágenes de la cátedra con
`scripts/calibrate_stereo.py`, RMS 1,055 px, 20 de 21 pares) y `stereo_maps_720p.pkl`
(esa misma calibración escalada a 720p).

### Rectificación

Los 27 pares rectificados están en `datasets/stereo_stitch_charuco/rect/` como
`rect_left_N.png` / `rect_right_N.png` (PNG para no meter artefactos JPEG antes del
matching), junto con `stereodemo_calibration.json`. La carpeta está en `.gitignore`
porque pesa; se regenera en segundos con:

```bash
python scripts/rectify.py --calib stereo_calibration.pkl \
    --maps stereo_maps.pkl \
    --captures datasets/stereo_stitch_charuco/captures \
    --out datasets/stereo_stitch_charuco/rect
```

El script además mide la calidad de la rectificación emparejando features SIFT entre
izquierda y derecha y mirando cuánto difieren en vertical (deberían estar en la misma
fila). Resultado con la calibración propia:

| Par | mediana \|dy\| | p90 \|dy\| | disparidad p05 a p95 |
|---|---|---|---|
| 0 | 1,37 px | 2,29 px | 21 a 96 px |
| 10 | 0,67 px | 1,52 px | 36 a 95 px |
| 25 | 0,31 px | 0,83 px | 37 a 63 px |

Es aceptable para SGBM. Dato para la discusión: la calibración de la cátedra escalada
daba 0,2 a 0,6 px, así que si volvemos a tener la cámara conviene recalibrar con más
vistas cubriendo bordes y esquinas.

## 4. El tablero ChArUco (pendiente de resolver, bloquea 4.2.3)

El tablero que usamos **no es el `5x7 / 52.6 mm / DICT_6X6_250`** del `markers.yaml` de la
cátedra. Lo que sabemos por detección sobre las capturas:

- Diccionario: **DICT_5X5** (con `DICT_5X5_250` se detectan 20 a 36 marcadores por
  imagen; con 6X6 no se detecta nada).
- IDs vistos hasta el **57**, así que el tablero tiene al menos 58 marcadores, es decir
  al menos ~116 casilleros. Es bastante más grande que 5x7. La cantidad exacta de
  casilleros por lado todavía no está determinada.
- **Hace falta medir físicamente** el tablero: cantidad de casilleros en cada eje, lado
  del casillero en mm y lado del marcador en mm. Con eso se crea el `markers.yaml` y
  el `CharucoBoard` para la pose. Si ya no tenemos el tablero, se puede recuperar el
  tamaño del casillero triangulando sus esquinas con la calibración métrica, pero la
  regla es mejor.

## 5. Lo que sigue: disparidad (etapa 4.2.1)

Idea central: los parámetros del matcher dependen de la cámara y la escena, no de cada
foto. Se eligen una vez sobre dos o tres pares representativos y se aplican a los 27.

1. Abrir la tool interactiva sobre la carpeta rectificada (ya quedó todo armado):
   ```bash
   cd tp2_reconstruccion_3d
   stereodemo datasets/stereo_stitch_charuco/rect
   ```
   Tiene botón "Next Image" para pasar de par, sliders por método y vista 3D.
2. Orden sugerido de ajuste: `numDisparities` por geometría (la disparidad observada
   va de ~7 a ~100 px, así que **128**); después `blockSize`/`P1`/`P2` mirando el cuerpo
   del peluche; por último `uniquenessRatio`/`speckle*` mirando que el fondo quede limpio.
3. Anotar los valores finales en un archivo del repo (propuesta: `config/disparity_params.json`
   con los nombres de parámetros de OpenCV) y escribir el script que lo lee y procesa
   los 27 pares, guardando cada disparidad como `.npy` float32 (no PNG de 8 bits) más una
   vista previa coloreada. **Esto todavía no está escrito.**

Punto de partida razonable para SGBM: `numDisparities=128, blockSize=5, P1=200, P2=800,
uniquenessRatio=10, speckleWindowSize=200, speckleRange=2, disp12MaxDiff=1,
preFilterCap=63, mode=SGBM_3WAY`. Para probar CREStereo (red neuronal), el paquete
`disparity` de `code_examples/stereodemo_disp_example/` lo envuelve con la misma interfaz
que BM y SGBM.

Relación disparidad-profundidad con nuestra calibración: z = f·B / d ≈ 24400 / d
(z en mm, d en px). El peluche está a unos 25 a 60 cm, o sea d entre ~40 y ~100 px.

Detalles que muerden: OpenCV devuelve la disparidad x16 en int16 (dividir por 16);
los inválidos salen negativos (enmascarar con `d > 0`); la franja izquierda de ancho
`numDisparities` nunca tiene disparidad válida.

## 6. Entorno

Se está usando el Python de miniconda (3.13) con: opencv-python y opencv-contrib 4.13,
open3d 0.20, stereodemo 0.7, onnxruntime. Hubo que actualizar `libstdcxx` en conda para
que Open3D importe (error `GLIBCXX_3.4.30 not found`); si a alguien le pasa lo mismo:
`conda install -c conda-forge "libstdcxx-ng>=12" "libgcc-ng>=12"`. Para el entregable
falta armar `requirements.txt` con versiones.

## 7. Estado real del repo y errores corregidos (10/10/2026)

- **Corregido** `notebooks/tp2.ipynb`: usaba claves inexistentes del pkl (`map_l_1`...; las
  reales son `left_map_x/y`, `right_map_x/y`), rutas de ejemplo (`captures/objeto_left_01.jpg`)
  y la celda de StereoBM usaba variables sin definir (`left_image_rectified`). Ahora carga
  `stereo_maps.pkl` y el par `left_N/right_N` de `datasets/stereo_stitch_charuco/captures`,
  rectifica, y calcula SGBM y BM (disparidad en float, inválidos en NaN). Probado: ~56 %
  de píxeles con disparidad válida en el par 0.
- **Ojo**: `scripts/`, `calibration/`, `rect/` y `.gitignore` que se describen abajo
  **no existen en este checkout** (hay que recuperarlos o reescribirlos). Los `.pkl` están
  en la raíz y sin ignorar. `stereo_maps.pkl` pesa 14 MB; decidir si va al repo.
- Pendiente de limpieza: el `git status` tiene borrados de `datasets/stereo_budha_charuco/`
  y modificaciones en `code_examples/` (probablemente saltos de línea CRLF por Windows).

## 8. Plan de trabajo (próximos pasos, en orden)

1. **Recalcular el RMS de calibración** (lo pide el informe) con `cv2.stereoCalibrate`
   sobre `datasets/stereo_stitch_charuco/calib/` (checkerboard 10x7, 24,2 mm).
2. **Script de disparidad** `src/disparity.py`: lee los 27 pares, rectifica, corre SGBM con
   parámetros en `config/disparity_params.json`, guarda `.npy` float32 + PNG coloreado.
   Afinar antes con `stereodemo` en 2 o 3 pares; probar también CREStereo.
3. **Nube local** (4.2.2): `cv2.reprojectImageTo3D(disp, Q)`, máscara `disp > 0` y rango de z
   (250 a 600 mm), guardar `.ply` por par. Chequeo: z ≈ 24400 / d.
4. **Medir el tablero ChArUco** (casilleros por eje, lado del casillero y del marcador en mm,
   diccionario DICT_5X5_250) y crear `markers.yaml`. **Bloquea 4.2.3**.
5. **Pose por par** con `CharucoBoard` + `solvePnP` (4.2.3) y transformación de cada nube al
   marco del tablero (4.2.4). Descartar pares donde la pose tenga alto error de reproyección.
6. **Fusión en Open3D** (4.3): voxel downsample, remoción de outliers, ICP de refinamiento,
   Poisson o ball pivoting para la malla.
7. **Medición métrica** (sección 5 del enunciado) sobre el modelo fusionado y comparación
   contra una medida real del peluche.
8. **Entregable**: `requirements.txt` con versiones, informe con RMS, tablas de parámetros
   y resultados.

## 9. Archivos descritos originalmente (verificar si existen)

- `scripts/calibrate_stereo.py`: calibración estéreo desde una carpeta de pares de
  checkerboard, estilo Tutorial 6. Guarda un pkl con las mismas claves que la tool.
- `scripts/rectify.py`: rectifica una carpeta de capturas (con mapas existentes o
  calculándolos), genera el json de stereodemo y corre el chequeo epipolar.
- `calibration/`: los pkl descritos arriba.
- `.gitignore`: excluye `rect/`, `*_maps*.pkl`, `*.npy`, `__pycache__/`, `.venv/`.
