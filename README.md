# TP2 - Reconstrucción 3D

I308 Visión Artificial, Universidad de San Andrés (2026). Luis Embon Strizzi, Franco Sandri y Alan Yeger.

Reconstrucción 3D de un peluche de Stitch a partir de 27 pares estéreo tomados en órbita
alrededor del objeto, con la cámara ELP-USB3D1080P02 de la cátedra (modo 2560x720) y un
tablero ChArUco como marco global. El pipeline calibra y rectifica el sistema estéreo,
calcula la disparidad con SGBM, convierte cada par en una nube local, estima la pose de la
cámara con `solvePnP` sobre el tablero, lleva todas las nubes al marco del tablero, las
fusiona y optimiza en Open3D y mide el objeto en milímetros.

## Resultados

| | Estimado | Real (regla) | Error relativo |
|---|---|---|---|
| Alto | 279,7 mm | 290 mm | −3,5 % |
| Ancho (orejas) | 294,0 mm | 300 mm | −2,0 % |
| Profundidad | 172,5 mm | 170 mm | +1,4 % |

- Calibración estéreo: error de reproyección RMS 1,25 px, baseline 60,17 mm.
- Nube final: 175 791 puntos, `.ply` binario de 4,7 MB (`outputs/stitch_final.ply`).

## Estructura

```
notebooks/
  tp2.ipynb          pipeline completo, de la calibración a la medición
  utils.py           funciones auxiliares (lectura, ChArUco, pose, disparidad, nubes, gráficos)
calibration/
  stereo_calibration.pkl, stereo_maps.pkl   salida de la tool calib-stereo (1280x720)
datasets/
  calib/                          30 pares del checkerboard usados para calibrar (9x6 esquinas, casillero 28 mm)
  stereo_stitch_charuco/captures  27 pares crudos del peluche sobre el ChArUco
  stereo_stitch_charuco/rect      los mismos pares rectificados (los genera el notebook) y el json de stereodemo
  stereo_budha_board/, stereo_stitch_charuco/calib/   material de la cátedra, no se usa
outputs/
  stitch_final.ply   nube final optimizada (entregable)
imgs/                capturas de stereodemo (SGBM vs CREStereo) y de MeshLab
informe/             informe en LaTeX y sus figuras
code_examples/       ejemplos provistos por la cátedra
```

## Instalación

Probado con Python 3.13 en Linux (WSL, Ubuntu 22.04).

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Las versiones están fijadas en `requirements.txt`. OpenCV 4.12 rompe el módulo ArUco: usar
4.11 o 4.13. Si Open3D falla con `GLIBCXX_3.4.30 not found` en conda, instalar
`libstdcxx-ng>=12` y `libgcc-ng>=12` de conda-forge.

## Uso

El notebook importa `utils.py` con `from utils import ...`, así que hay que abrirlo con
`notebooks/` como directorio de trabajo:

```bash
cd notebooks
pip install jupyterlab           # solo si no se usa VS Code
jupyter lab tp2.ipynb            # o abrirlo en VS Code con el kernel del entorno
```

Corriendo todas las celdas en orden (unos minutos) se reproducen la calibración, las
figuras de cada etapa, el `.ply` en `outputs/stitch_final.ply` y la medición. La última
celda abre visualizaciones interactivas de Open3D si se pone `SHOW_3D = True`.

Para ajustar los parámetros de disparidad de forma interactiva (requiere `stereodemo`,
ver `requirements.txt`), desde la raíz del repo y después de correr el notebook:

```bash
stereodemo datasets/stereo_stitch_charuco/rect
```

La nube final se puede abrir con [MeshLab](https://www.meshlab.net/).

## Entregables

- Informe: `informe/embon_sandri_yeger-tp2-informe.tex`.
- Nube final: `outputs/stitch_final.ply`
  ([descarga directa](https://drive.google.com/uc?export=download&id=1Ybi883HTbzfYiLK3ib5xr77Oo-P2mrJS),
  4,7 MB).
- Dataset propio: `datasets/calib/` y `datasets/stereo_stitch_charuco/captures/`
  ([descarga directa del zip](https://drive.google.com/uc?export=download&id=1MptTQNZ2Sqe5Pskws_koW8t22n-sc9yt),
  23 MB). Descomprimido en la raíz del repo, cada carpeta queda en su lugar. Los pares
  rectificados de `rect/` no están en el zip porque los genera el notebook.
- Carpeta de Drive con los dos archivos:
  [Dataset-tp2-reconstruccion-3d](https://drive.google.com/drive/folders/1YVeUoTn8iDGOQCYMBNBdYpeawiBg1VgT?usp=sharing).
