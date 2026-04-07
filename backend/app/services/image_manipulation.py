"""Image manipulation service: speech bubbles + WhatsApp sticker generation."""
from __future__ import annotations

import os
import textwrap
from collections import deque
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont


# ── Font helpers ──────────────────────────────────────────────────────────────

_FONT_CANDIDATES = [
    "C:\\Windows\\Fonts\\arialbd.ttf",   # Arial Bold (Windows)
    "C:\\Windows\\Fonts\\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _load_font(size: int, font_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
    candidates = ([font_path] if font_path else []) + _FONT_CANDIDATES
    for path in candidates:
        if path and os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ── Background removal ───────────────────────────────────────────────────────

def remove_background(image: Image.Image, tolerance: int = 30) -> Image.Image:
    """
    Remove the background of *image* using a flood-fill from all four corners.

    Works well for cartoon/sticker images that have a solid or near-solid background.
    Returns an RGBA image with the background made transparent.

    Args:
        image:     Input PIL image (any mode).
        tolerance: Max color distance (per channel) to consider a pixel as background.
                   Higher values remove more; lower values are more conservative.
    """
    img = image.convert("RGBA")
    w, h = img.size
    pixels = img.load()

    def color_distance(c1: tuple, c2: tuple) -> int:
        return max(abs(int(c1[i]) - int(c2[i])) for i in range(3))

    # Sample background color from the four corners
    corners = [pixels[0, 0], pixels[w - 1, 0], pixels[0, h - 1], pixels[w - 1, h - 1]]
    # Use the most common corner color (mode of R+G+B average)
    bg_color = min(corners, key=lambda c: sum(c[:3]))  # darkest corner → least likely to be art

    # Prefer a lighter corner as background (white/gray backgrounds are most common)
    bg_color = max(corners, key=lambda c: sum(c[:3]))

    visited = set()
    queue: deque = deque()

    # Seed flood-fill from all four corners
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for sx, sy in seeds:
        if (sx, sy) not in visited and color_distance(pixels[sx, sy], bg_color) <= tolerance:
            queue.append((sx, sy))
            visited.add((sx, sy))

    while queue:
        x, y = queue.popleft()
        # Make transparent
        r, g, b, a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)

        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if color_distance(pixels[nx, ny], bg_color) <= tolerance:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    # Smooth the alpha edge with a slight blur on the alpha channel
    r, g, b, a = img.split()
    a = a.filter(ImageFilter.SMOOTH)
    return Image.merge("RGBA", (r, g, b, a))


# ── Text helpers ──────────────────────────────────────────────────────────────

def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap *text* so each rendered line fits within *max_width* pixels."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        w = font.getbbox(candidate)[2] - font.getbbox(candidate)[0]
        if w <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _measure_lines(lines: list[str], font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """Return (max_line_width, total_height) for a list of lines."""
    line_height = font.getbbox("Ag")[3] - font.getbbox("Ag")[1] + 4
    max_w = max((font.getbbox(l)[2] - font.getbbox(l)[0]) for l in lines)
    total_h = line_height * len(lines) - 4
    return max_w, total_h


# ── Bubble drawing ────────────────────────────────────────────────────────────

def _draw_rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    radius: int,
    fill: Tuple[int, int, int, int],
    outline: Tuple[int, int, int, int],
    border: int,
) -> None:
    """Properly filled rounded rectangle with outline."""
    x1, y1, x2, y2 = box
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

    # Fill body
    draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
    draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)
    draw.pieslice([x1,       y1,       x1 + 2*r, y1 + 2*r], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*r, y1,       x2,       y1 + 2*r], 270, 360, fill=fill)
    draw.pieslice([x2 - 2*r, y2 - 2*r, x2,       y2      ], 0,   90,  fill=fill)
    draw.pieslice([x1,       y2 - 2*r, x1 + 2*r, y2      ], 90,  180, fill=fill)

    # Outline — draw the same shape with no fill, thick line
    for i in range(border):
        bx1, by1, bx2, by2 = x1 + i, y1 + i, x2 - i, y2 - i
        br = max(r - i, 0)
        draw.arc([bx1,          by1,          bx1 + 2*br, by1 + 2*br], 180, 270, outline)
        draw.arc([bx2 - 2*br,   by1,          bx2,        by1 + 2*br], 270, 360, outline)
        draw.arc([bx2 - 2*br,   by2 - 2*br,   bx2,        by2       ], 0,   90,  outline)
        draw.arc([bx1,          by2 - 2*br,   bx1 + 2*br, by2       ], 90,  180, outline)
        draw.line([bx1 + br, by1, bx2 - br, by1],    fill=outline)
        draw.line([bx1 + br, by2, bx2 - br, by2],    fill=outline)
        draw.line([bx1, by1 + br, bx1, by2 - br],    fill=outline)
        draw.line([bx2, by1 + br, bx2, by2 - br],    fill=outline)


def _draw_tail(
    draw: ImageDraw.ImageDraw,
    bubble_box: Tuple[int, int, int, int],
    tail_size: int,
    fill: Tuple[int, int, int, int],
    outline: Tuple[int, int, int, int],
    border: int,
    tail_x_ratio: float = 0.3,
) -> None:
    """
    Draw the speech-bubble tail pointing DOWNWARD from the bottom of the bubble.
    *tail_x_ratio* (0‥1) controls where along the bottom edge the tail originates.
    """
    x1, y1, x2, y2 = bubble_box
    tip_x = int(x1 + (x2 - x1) * tail_x_ratio)
    base_half = tail_size // 2

    tail_poly = [
        (tip_x - base_half, y2),
        (tip_x + base_half, y2),
        (tip_x,             y2 + tail_size),
    ]
    draw.polygon(tail_poly, fill=fill)
    draw.polygon(tail_poly, outline=outline)
    # Thicken outline
    for _ in range(border - 1):
        draw.polygon(tail_poly, outline=outline)


def _draw_text_in_bubble(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    bubble_box: Tuple[int, int, int, int],
    text_color: Tuple[int, int, int, int],
    padding: int,
) -> None:
    x1, y1, x2, y2 = bubble_box
    inner_w = x2 - x1 - 2 * padding
    inner_h = y2 - y1 - 2 * padding
    line_height = font.getbbox("Ag")[3] - font.getbbox("Ag")[1] + 4
    total_h = line_height * len(lines) - 4
    start_y = y1 + padding + (inner_h - total_h) // 2

    for i, line in enumerate(lines):
        lw = font.getbbox(line)[2] - font.getbbox(line)[0]
        lx = x1 + padding + (inner_w - lw) // 2
        ly = start_y + i * line_height
        draw.text((lx, ly), line, font=font, fill=text_color)


# ── Placeholder avatar generator ─────────────────────────────────────────────

#: Paleta por emoción: (bg_hex, head_hex)
_EMOTION_PALETTE: dict[str, tuple[str, str]] = {
    "risa":      ("#FFD700", "#FFA500"),
    "sorpresa":  ("#FF69B4", "#FFB6C1"),
    "enojo":     ("#FF4444", "#FF8888"),
    "tristeza":  ("#4488FF", "#99BBFF"),
    "confusión": ("#9966CC", "#CC99FF"),
    "sarcasmo":  ("#888888", "#BBBBBB"),
}
_DEFAULT_PALETTE = ("#FFFFFF", "#AAAAAA")


def _hex(color: str) -> tuple[int, int, int, int]:
    """Convert #RRGGBB string to RGBA tuple (alpha=255)."""
    h = color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def generate_placeholder_avatar(emotion: str) -> Image.Image:
    """
    Generate a simple 300×300 cartoon face for *emotion* using only PIL.

    Faces are: colored background, circular head, two dot eyes, and an
    emotion-specific mouth.  Good enough for MVP / missing-asset fallback.

    Supported emotions: risa, sorpresa, enojo, tristeza, confusión, sarcasmo.
    Any other value produces a neutral face on white background.
    """
    size = 300
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg_hex, head_hex = _EMOTION_PALETTE.get(emotion.lower(), _DEFAULT_PALETTE)
    bg_color   = _hex(bg_hex)
    head_color = _hex(head_hex)
    outline    = (30, 30, 30, 255)

    # Background
    draw.rectangle([0, 0, size, size], fill=bg_color)

    # Head circle  (centred, ~55% of canvas)
    cx, cy = size // 2, size // 2
    r = int(size * 0.27)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=head_color, outline=outline, width=3)

    # Eyes (two filled circles, symmetric)
    ex_off, ey_off = int(r * 0.38), int(r * 0.30)
    er = max(4, int(r * 0.10))
    for ex in [cx - ex_off, cx + ex_off]:
        ey = cy - ey_off
        draw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=outline)

    # Mouth — shape depends on emotion
    mw, my = int(r * 0.55), cy + int(r * 0.35)  # mouth half-width, mouth y center
    stroke = max(3, int(r * 0.09))

    em = emotion.lower()

    if em == "risa":
        # Wide U-shaped smile
        draw.arc([cx - mw, my - mw // 2, cx + mw, my + mw // 2],
                 start=0, end=180, fill=outline, width=stroke)

    elif em == "sorpresa":
        # Open O mouth
        om = max(6, int(r * 0.18))
        draw.ellipse([cx - om, my - om, cx + om, my + om],
                     fill=(255, 200, 150, 255), outline=outline, width=stroke)

    elif em == "enojo":
        # Straight tight line + furrowed V brows
        draw.line([cx - mw, my, cx + mw, my], fill=outline, width=stroke)
        bw = int(r * 0.35)
        by = cy - int(r * 0.55)
        for sign in (-1, 1):
            bx = cx + sign * int(r * 0.38)
            draw.line(
                [bx - sign * bw // 2, by - int(r * 0.12),
                 bx + sign * bw // 2, by + int(r * 0.12)],
                fill=outline, width=stroke,
            )

    elif em == "tristeza":
        # Inverted arc (frown)
        draw.arc([cx - mw, my - mw // 2, cx + mw, my + mw // 2],
                 start=180, end=360, fill=outline, width=stroke)

    elif em == "confusión":
        # Question mark drawn with text (large, centred)
        font = _load_font(int(r * 0.9))
        bbox = font.getbbox("?")
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(
            (cx - tw // 2, cy - th // 2),
            "?", font=font, fill=outline,
        )

    elif em == "sarcasmo":
        # Asymmetric smirk: left side up, right side level
        draw.line([cx - mw, my - stroke, cx, my], fill=outline, width=stroke)
        draw.line([cx, my, cx + mw, my + stroke],  fill=outline, width=stroke)

    else:
        # Neutral flat line
        draw.line([cx - mw, my, cx + mw, my], fill=outline, width=stroke)

    return img


# ── Main public function ──────────────────────────────────────────────────────

def generate_sticker(
    base_image: Image.Image,
    text: str,
    *,
    output_path: Optional[str] = None,
    output_format: str = "WEBP",       # "WEBP" or "PNG"
    canvas_size: int = 512,            # WhatsApp requires 512×512
    bubble_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    border_color: Tuple[int, int, int, int] = (20, 20, 20, 255),
    text_color: Tuple[int, int, int, int] = (20, 20, 20, 255),
    border_width: int = 3,
    corner_radius: int = 18,
    tail_size: int = 18,
    tail_x_ratio: float = 0.3,
    padding: int = 14,
    font_path: Optional[str] = None,
    font_size: Optional[int] = None,   # auto if None
    bubble_top_margin: int = 12,       # px from top of canvas to bubble top
    max_bubble_height_ratio: float = 0.38,  # bubble may use at most 38% of canvas height
) -> Image.Image:
    """
    Compose a WhatsApp-style sticker:

    - Transparent 512×512 canvas (RGBA)
    - Base image (character) centered at the bottom half
    - Comic speech bubble (white, black border) in the top area
    - Text auto-wrapped to fit inside the bubble
    - Pointed tail from bubble bottom toward the character

    Args:
        base_image: PIL Image of the avatar/character.
        text:       Text to show in the speech bubble.
        output_path: If given, the result is also saved here.
        output_format: "WEBP" (default, WhatsApp) or "PNG".
        canvas_size: Side length of the square canvas (default 512).
        bubble_color: RGBA fill for the bubble.
        border_color: RGBA outline color.
        text_color:  RGBA text color.
        border_width: Border stroke width in pixels.
        corner_radius: Rounded corner radius.
        tail_size:   Height of the triangular tail.
        tail_x_ratio: Horizontal position of tail along bubble bottom (0=left, 1=right).
        padding:     Inner padding between bubble edge and text.
        font_path:   Path to a .ttf font (auto-detected if None).
        font_size:   Font size in px (auto-scaled from text length if None).
        bubble_top_margin: Gap between canvas top and bubble top.
        max_bubble_height_ratio: Max fraction of canvas the bubble can occupy.

    Returns:
        RGBA PIL Image ready to send as sticker.
    """

    # ── 1. Canvas ────────────────────────────────────────────────────────────
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    # ── 2. Paste character image (bottom-center, takes ~60% of height) ───────
    char_area_h = int(canvas_size * 0.62)
    char_area_w = canvas_size

    char = remove_background(base_image)
    # Recortar el padding transparente para que thumbnail y posición sean exactos
    bbox = char.getbbox()
    if bbox:
        char = char.crop(bbox)
    char.thumbnail((char_area_w, char_area_h), Image.LANCZOS)
    char_x = (canvas_size - char.width) // 2
    char_y = canvas_size - char.height          # flush with bottom
    canvas.paste(char, (char_x, char_y), char)

    # Top visual del personaje en el canvas — aquí apunta la cola del globo
    char_visual_top = char_y

    # ── 3. Font & auto-size ──────────────────────────────────────────────────
    bubble_max_w = int(canvas_size * 0.82)

    if font_size is None:
        # Scale font down for longer texts
        font_size = 26 if len(text) <= 40 else (22 if len(text) <= 80 else 18)

    font = _load_font(font_size, font_path)

    # ── 4. Wrap text to fit inside the bubble ────────────────────────────────
    inner_max_w = bubble_max_w - 2 * padding
    lines = _wrap_text(text, font, inner_max_w)
    _, text_h = _measure_lines(lines, font)
    bubble_h = text_h + 2 * padding

    # Clamp bubble height to max_bubble_height_ratio
    max_bh = int(canvas_size * max_bubble_height_ratio) - tail_size
    if bubble_h > max_bh:
        # Reduce font until it fits
        while bubble_h > max_bh and font_size > 10:
            font_size -= 1
            font = _load_font(font_size, font_path)
            lines = _wrap_text(text, font, inner_max_w)
            _, text_h = _measure_lines(lines, font)
            bubble_h = text_h + 2 * padding

    # ── 5. Bubble geometry ────────────────────────────────────────────────────
    bubble_w = min(bubble_max_w, max(
        int(_measure_lines(lines, font)[0] + 2 * padding + 16),
        bubble_max_w // 2,
    ))
    bx1 = (canvas_size - bubble_w) // 2
    bx2 = bx1 + bubble_w

    # Posicionar el globo justo encima del personaje (con 8px de margen entre cola y cabeza)
    by2 = char_visual_top - tail_size - 8
    by2 = max(by2, bubble_top_margin + bubble_h)   # nunca salirse del canvas por arriba
    by1 = by2 - bubble_h
    bubble_box = (bx1, by1, bx2, by2)

    # ── 6. Draw bubble on canvas ─────────────────────────────────────────────
    draw = ImageDraw.Draw(canvas)

    _draw_rounded_rect(draw, bubble_box, corner_radius, bubble_color, border_color, border_width)
    _draw_tail(draw, bubble_box, tail_size, bubble_color, border_color, border_width, tail_x_ratio)
    _draw_text_in_bubble(draw, lines, font, bubble_box, text_color, padding)

    # ── 7. Save & return ──────────────────────────────────────────────────────
    if output_path:
        fmt = output_format.upper()
        save_kwargs = {"format": fmt}
        if fmt == "WEBP":
            save_kwargs.update({"quality": 90, "method": 6})
        canvas.save(output_path, **save_kwargs)

    return canvas


# ── Backwards-compatible wrappers ─────────────────────────────────────────────

class SpeechBubbleStyle:
    """Legacy config object kept for backwards compatibility."""

    def __init__(
        self,
        bubble_color: Tuple[int, int, int] = (255, 255, 255),
        text_color: Tuple[int, int, int] = (0, 0, 0),
        border_color: Tuple[int, int, int] = (0, 0, 0),
        border_width: int = 3,
        padding: int = 14,
        corner_radius: int = 18,
        tail_size: int = 18,
        tail_position: str = "bottom-left",
        bubble_style: str = "comic",
    ):
        self.bubble_color  = bubble_color
        self.text_color    = text_color
        self.border_color  = border_color
        self.border_width  = border_width
        self.padding       = padding
        self.corner_radius = corner_radius
        self.tail_size     = tail_size
        self.tail_position = tail_position
        self.bubble_style  = bubble_style


class ImageWithSpeechBubble:
    """Legacy class — delegates to generate_sticker()."""

    @staticmethod
    def add_speech_bubble_from_image(
        image: Image.Image,
        text: str,
        style: Optional[SpeechBubbleStyle] = None,
        bubble_position: str = "top",
        bubble_width_ratio: float = 0.82,
        font_size: int = 22,
        font_path: Optional[str] = None,
    ) -> Image.Image:
        s = style or SpeechBubbleStyle()
        result = generate_sticker(
            image,
            text,
            bubble_color=(*s.bubble_color, 255),
            border_color=(*s.border_color, 255),
            text_color=(*s.text_color, 255),
            border_width=s.border_width,
            corner_radius=s.corner_radius,
            tail_size=s.tail_size,
            padding=s.padding,
            font_path=font_path,
            font_size=font_size,
        )
        # Return RGB (without alpha) to preserve existing behavior
        bg = Image.new("RGB", result.size, (255, 255, 255))
        bg.paste(result, mask=result.split()[3])
        return bg

    @staticmethod
    def add_speech_bubble(
        image_path: str,
        text: str,
        output_path: Optional[str] = None,
        style: Optional[SpeechBubbleStyle] = None,
        bubble_position: str = "top",
        bubble_width_ratio: float = 0.82,
        font_size: int = 22,
        font_path: Optional[str] = None,
    ) -> Image.Image:
        image = Image.open(image_path)
        return ImageWithSpeechBubble.add_speech_bubble_from_image(
            image, text, style, bubble_position, bubble_width_ratio, font_size, font_path
        )


def add_speech_bubble(
    image_path: str,
    text: str,
    output_path: Optional[str] = None,
    bubble_position: str = "top",
    font_size: int = 22,
) -> Image.Image:
    """Convenience function — kept for backwards compatibility."""
    return ImageWithSpeechBubble.add_speech_bubble(
        image_path, text, output_path, bubble_position=bubble_position, font_size=font_size
    )
