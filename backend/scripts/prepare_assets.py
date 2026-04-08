"""
prepare_assets.py
Procesa las imágenes del gato desde assets/poses/ del root del monorepo:
  1. Remueve el fondo blanco → transparente (flood fill desde esquinas, tolerancia 30)
  2. Redimensiona a 300x300 manteniendo aspect ratio con padding transparente
  3. Guarda en backend/assets/poses/ con los nombres del sistema de emociones
"""
from __future__ import annotations

from pathlib import Path
from collections import deque
from PIL import Image

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT        = Path(__file__).parent.parent.parent          # raíz del monorepo
SRC_DIR     = ROOT / "assets" / "poses"                    # imágenes originales
DST_DIR     = Path(__file__).parent.parent / "assets" / "poses"  # backend/assets/poses
DST_DIR.mkdir(parents=True, exist_ok=True)

# ── Mapeo nombre_original → nombre_sistema ────────────────────────────────────

MAPPING = {
    "feliz.png":       "risa.png",
    "enojado.png":     "enojo.png",
    "sorpresa.png":    "sorpresa.png",
    "lloroso.png":     "tristeza.png",
    "confundido.png":  "confusión.png",
    "dealwithit.png":  "sarcasmo.png",
    # extras — se guardan con su nombre original para uso futuro
    "celebra.png":     "celebra.png",
    "confiado.png":    "confiado.png",
    "aburrido.png":    "aburrido.png",
    "distraido.png":   "distraido.png",
}

TARGET_SIZE = (300, 300)
TOLERANCE   = 30   # tolerancia para flood fill del fondo blanco


# ── Helpers ───────────────────────────────────────────────────────────────────

def _color_distance(c1: tuple, c2: tuple) -> float:
    """Distancia euclidiana entre dos colores RGB."""
    return sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3])) ** 0.5


def remove_white_background(img: Image.Image, tolerance: int = TOLERANCE) -> Image.Image:
    """
    Flood fill desde las 4 esquinas para detectar el fondo blanco y
    convertirlo a transparente. Funciona bien con imágenes estilo sticker
    que tienen fondo blanco uniforme.
    """
    img = img.convert("RGBA")
    data = img.load()
    width, height = img.size

    # Color de referencia: promedio de las 4 esquinas
    corners = [
        data[0, 0][:3],
        data[width - 1, 0][:3],
        data[0, height - 1][:3],
        data[width - 1, height - 1][:3],
    ]
    bg_color = tuple(sum(c[i] for c in corners) // 4 for i in range(3))

    visited = [[False] * height for _ in range(width)]
    queue   = deque()

    # Sembrar desde las 4 esquinas
    seeds = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    for sx, sy in seeds:
        if not visited[sx][sy]:
            queue.append((sx, sy))
            visited[sx][sy] = True

    while queue:
        x, y = queue.popleft()
        r, g, b, a = data[x, y]
        if _color_distance((r, g, b), bg_color) <= tolerance:
            data[x, y] = (r, g, b, 0)   # transparente
            for nx, ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if 0 <= nx < width and 0 <= ny < height and not visited[nx][ny]:
                    visited[nx][ny] = True
                    queue.append((nx, ny))

    return img


def fit_to_canvas(img: Image.Image, size: tuple = TARGET_SIZE) -> Image.Image:
    """
    Redimensiona manteniendo aspect ratio y centra sobre un canvas
    transparente de 'size'.
    """
    img.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    canvas.paste(img, offset, img if img.mode == "RGBA" else None)
    return canvas


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Source : {SRC_DIR}")
    print(f"Dest   : {DST_DIR}")
    print(f"Canvas : {TARGET_SIZE[0]}x{TARGET_SIZE[1]}px\n")

    processed = 0
    errors    = 0

    for src_name, dst_name in MAPPING.items():
        src_path = SRC_DIR / src_name
        dst_path = DST_DIR / dst_name

        if not src_path.exists():
            print(f"  SKIP {src_name} (no encontrado en {SRC_DIR})")
            continue

        try:
            img    = Image.open(src_path)
            img    = remove_white_background(img)
            img    = fit_to_canvas(img)
            img.save(dst_path, format="PNG")
            print(f"  OK   {src_name:20s} -> {dst_name}")
            processed += 1
        except Exception as e:
            print(f"  ERR  {src_name:20s} ERROR: {e}")
            errors += 1

    print(f"\nResultado: {processed} procesadas, {errors} errores")
    print(f"Archivos en {DST_DIR}:")
    for f in sorted(DST_DIR.iterdir()):
        size_kb = f.stat().st_size // 1024
        print(f"  {f.name:30s} {size_kb} KB")


if __name__ == "__main__":
    main()
