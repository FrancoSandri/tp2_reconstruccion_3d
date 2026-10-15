import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


# cv2.imread devuelve None con rutas no ASCII en Windows (ej. "Visión"),
# por eso leemos y escribimos las imágenes con numpy
def read_img(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe {path}")
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"No se pudo decodificar {path}")
    return img


def write_img(path, img):
    ok, buf = cv2.imencode(os.path.splitext(path)[1], img)
    if not ok:
        raise ValueError(f"No se pudo codificar {path}")
    buf.tofile(path)


# número de captura a partir del nombre del archivo (left_13.jpg -> 13)
def numero(path):
    return int(os.path.basename(path).split("_")[-1].split(".")[0])


def rectify_pair(idx, captures_dir, maps):
    l = read_img(os.path.join(captures_dir, f"left_{idx}.jpg"))
    r = read_img(os.path.join(captures_dir, f"right_{idx}.jpg"))
    l_rect = cv2.remap(l, maps["left_map_x"], maps["left_map_y"], cv2.INTER_LINEAR)
    r_rect = cv2.remap(r, maps["right_map_x"], maps["right_map_y"], cv2.INTER_LINEAR)
    return l, l_rect, r_rect


# devuelve {id_esquina: (u, v)} en la imagen original (sin rectificar)
def detect_charuco(img, charuco_detector):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    ch_corners, ch_ids, _, _ = charuco_detector.detectBoard(gray)
    if ch_ids is None:
        return {}
    return dict(zip(ch_ids.ravel().tolist(), ch_corners.reshape(-1, 2).astype(np.float64)))


# Pose del tablero en la cámara: X_cam = R_wc @ X_board + t_wc.
# IPPE (específico para puntos coplanares) + descarte iterativo de esquinas mal detectadas.
def estimate_pose(img, K, dist, charuco_detector, corners3d_board, min_corners=8):
    det = detect_charuco(img, charuco_detector)
    if len(det) < min_corners:
        return None

    ids = np.array(sorted(det))
    obj = corners3d_board[ids].astype(np.float64)
    img_pts = np.array([det[k] for k in ids])

    keep = np.ones(len(ids), bool)
    for _ in range(3):
        ok, rvec, tvec = cv2.solvePnP(obj[keep], img_pts[keep], K, dist, flags=cv2.SOLVEPNP_IPPE)
        rvec, tvec = cv2.solvePnPRefineLM(obj[keep], img_pts[keep], K, dist, rvec, tvec)

        # error de reproyección de cada esquina
        proj, _ = cv2.projectPoints(obj, rvec, tvec, K, dist)
        err = np.linalg.norm(proj.reshape(-1, 2) - img_pts, axis=1)

        # descartamos las esquinas con error alto y repetimos
        new_keep = err < max(2.0, 3 * np.median(err))
        if (new_keep == keep).all():
            break
        keep = new_keep
        if keep.sum() < min_corners:
            return None

    return {
        "rvec": rvec,
        "tvec": tvec,
        "n_det": len(ids),
        "n_used": int(keep.sum()),
        "rms": float(np.sqrt(np.mean(err[keep] ** 2))),
    }


# distancia entre cada esquina triangulada y sus vecinas de la derecha y de abajo
def square_sides(Xt, common, good, n_corners_x):
    pos = {k: j for j, k in enumerate(common)}
    sides = []
    for k in common:
        if not good[pos[k]]:
            continue
        neighbors = [k + n_corners_x]                 # vecina de abajo
        if k % n_corners_x != n_corners_x - 1:
            neighbors.append(k + 1)                   # vecina de la derecha (si no es fin de fila)
        for n in neighbors:
            if n in pos and good[pos[n]]:
                sides.append(np.linalg.norm(Xt[pos[k]] - Xt[pos[n]]))
    return sides


def rms(e):
    return float(np.sqrt(np.mean(np.square(e))))


# OpenCV devuelve la disparidad x16 en int16: dividimos por 16 y marcamos los inválidos con NaN
def compute_disparity(sgbm, left_rect, right_rect, min_disparity):
    disp = sgbm.compute(left_rect, right_rect).astype(np.float32) / 16.0
    disp[disp <= min_disparity] = np.nan
    return disp


# nube local en la cámara izquierda rectificada (mm), filtrando profundidad y bordes de profundidad
def local_cloud(disp, left_rect, Q, z_range=(150, 1000), edge_max_dd=3.0):
    d0 = np.nan_to_num(disp, nan=0.0)
    pts = cv2.reprojectImageTo3D(d0, Q)          # (H, W, 3) en mm

    # bordes de profundidad: max - min de la disparidad en una ventana de 5x5
    kernel = np.ones((5, 5), np.uint8)
    edges = (cv2.dilate(d0, kernel) - cv2.erode(d0, kernel)) > edge_max_dd

    z = pts[..., 2]
    mask = np.isfinite(disp) & ~edges & (z > z_range[0]) & (z < z_range[1])

    colors = left_rect[mask][:, ::-1].astype(np.float32) / 255.0   # BGR -> RGB
    return pts[mask].astype(np.float64), colors, mask


# pirámide de la cámara izquierda (en mm) llevada al mundo
def frustum_world(view, K, image_size, scale=60.0):
    w, h = image_size
    Kinv = np.linalg.inv(K)
    rays = np.array([Kinv @ [u, v, 1.0] for u, v in [(0, 0), (w, 0), (w, h), (0, h)]]) * scale
    return view["center"], (rays - view["t_wc"]) @ view["R_wc"]


def to_pcd(X, C):
    import open3d as o3d
    p = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(X))
    p.colors = o3d.utility.Vector3dVector(C.astype(np.float64))
    return p


# vista de arriba, de frente y de costado de una nube
def plot_views(pcd, title, n=120_000):
    P, Cc = np.asarray(pcd.points), np.asarray(pcd.colors)
    s = np.random.default_rng(0).choice(len(P), min(n, len(P)), replace=False)

    fig, ax = plt.subplots(1, 3, figsize=(18, 5.5))
    for a, (i, j, t) in zip(ax, [(0, 1, "desde arriba (x, y)"), (0, 2, "frente (x, z)"), (1, 2, "costado (y, z)")]):
        a.scatter(P[s, i], P[s, j], c=Cc[s], s=0.4)
        a.set_title(t)
        a.set_aspect("equal")
        a.set_xlabel("xyz"[i] + " [mm]")
        a.set_ylabel("xyz"[j] + " [mm]")
    ax[1].invert_yaxis()
    ax[2].invert_yaxis()
    fig.suptitle(f"{title}: {len(P)} puntos")
    plt.show()
