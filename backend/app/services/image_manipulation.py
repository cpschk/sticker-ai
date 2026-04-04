"""Image manipulation service for adding speech bubbles to avatar poses"""
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
import os
import textwrap
from pathlib import Path


class SpeechBubbleStyle:
    """Speech bubble configuration"""
    
    def __init__(
        self,
        bubble_color: Tuple[int, int, int] = (255, 255, 255),
        text_color: Tuple[int, int, int] = (0, 0, 0),
        border_color: Tuple[int, int, int] = (0, 0, 0),
        border_width: int = 2,
        padding: int = 15,
        corner_radius: int = 15,
        tail_size: int = 15,
        tail_position: str = "bottom-left"  # bottom-left, bottom-right, top-left, top-right
    ):
        """
        Initialize speech bubble style
        
        Args:
            bubble_color: RGB tuple for bubble fill color
            text_color: RGB tuple for text color
            border_color: RGB tuple for border color
            border_width: Width of the border in pixels
            padding: Internal padding around text
            corner_radius: Radius of rounded corners
            tail_size: Size of the tail/pointer
            tail_position: Position of the tail
        """
        self.bubble_color = bubble_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.padding = padding
        self.corner_radius = corner_radius
        self.tail_size = tail_size
        self.tail_position = tail_position


class ImageWithSpeechBubble:
    """Service for adding speech bubbles to images"""
    
    @staticmethod
    def _wrap_text(text: str, max_chars: int = 40) -> str:
        """Wrap text to fit in max characters per line"""
        lines = []
        for line in text.split('\n'):
            if len(line) > max_chars:
                wrapped = textwrap.fill(line, width=max_chars)
                lines.extend(wrapped.split('\n'))
            else:
                lines.append(line)
        return '\n'.join(lines)
    
    @staticmethod
    def _get_text_size(text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
        """Get the size of text when rendered"""
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    @staticmethod
    def _draw_rounded_rectangle(
        draw: ImageDraw.ImageDraw,
        xy: Tuple[int, int, int, int],
        radius: int,
        fill: Tuple[int, int, int],
        outline: Tuple[int, int, int],
        width: int = 1
    ):
        """Draw a rounded rectangle"""
        x1, y1, x2, y2 = xy
        
        # Draw four corners
        draw.arc([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, outline, width)
        draw.arc([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, outline, width)
        draw.arc([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, outline, width)
        draw.arc([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, outline, width)
        
        # Draw connecting lines
        draw.line([(x1 + radius, y1), (x2 - radius, y1)], outline, width)
        draw.line([(x1 + radius, y2), (x2 - radius, y2)], outline, width)
        draw.line([(x1, y1 + radius), (x1, y2 - radius)], outline, width)
        draw.line([(x2, y1 + radius), (x2, y2 - radius)], outline, width)
        
        # Fill the rectangle
        draw.rectangle(
            [x1 + radius, y1, x2 - radius, y2],
            fill=fill
        )
        draw.rectangle(
            [x1, y1 + radius, x2, y2 - radius],
            fill=fill
        )
    
    @staticmethod
    def _draw_speech_bubble(
        image: Image.Image,
        xy: Tuple[int, int, int, int],
        text: str,
        style: SpeechBubbleStyle,
        font: Optional[ImageFont.FreeTypeFont] = None
    ) -> Image.Image:
        """Draw speech bubble on image"""
        
        draw = ImageDraw.Draw(image)
        x1, y1, x2, y2 = xy
        
        # Draw bubble background
        draw.polygon(
            [(x1, y1), (x2, y1), (x2, y2), (x1, y2)],
            fill=style.bubble_color
        )
        
        # Draw border
        draw.rectangle(
            xy,
            outline=style.border_color,
            width=style.border_width
        )
        
        # Draw tail
        tail_xoffset = (x2 - x1) // 3 if "left" in style.tail_position else 2 * (x2 - x1) // 3
        
        if "bottom" in style.tail_position:
            tail_points = [
                (x1 + tail_xoffset, y2),
                (x1 + tail_xoffset - style.tail_size, y2 + style.tail_size),
                (x1 + tail_xoffset + style.tail_size, y2 + style.tail_size),
            ]
        else:  # top
            tail_points = [
                (x1 + tail_xoffset, y1),
                (x1 + tail_xoffset - style.tail_size, y1 - style.tail_size),
                (x1 + tail_xoffset + style.tail_size, y1 - style.tail_size),
            ]
        
        draw.polygon(tail_points, fill=style.bubble_color)
        draw.polygon(tail_points, outline=style.border_color, width=style.border_width)
        
        # Draw text
        if font is None:
            font = ImageFont.load_default()
        
        text_x = x1 + style.padding
        text_y = y1 + style.padding
        
        draw.text(
            (text_x, text_y),
            text,
            fill=style.text_color,
            font=font
        )
        
        return image
    
    @staticmethod
    def add_speech_bubble(
        image_path: str,
        text: str,
        output_path: Optional[str] = None,
        style: Optional[SpeechBubbleStyle] = None,
        bubble_position: str = "top",
        bubble_width_ratio: float = 0.8,
        font_size: int = 20,
        font_path: Optional[str] = None
    ) -> Image.Image:
        """
        Add a speech bubble with text to an image
        
        Args:
            image_path: Path to the base image (avatar pose)
            text: Text to display in the bubble
            output_path: Path where to save the result (optional)
            style: SpeechBubbleStyle configuration (uses default if None)
            bubble_position: "top" or "bottom" position of the bubble
            bubble_width_ratio: Width of bubble as ratio of image (0.0-1.0)
            font_size: Size of the font
            font_path: Path to TrueType font file (uses default if None)
        
        Returns:
            Image object with speech bubble
            
        Example:
            >>> img = add_speech_bubble(
            ...     "avatar.png",
            ...     "Hola mundo!",
            ...     output_path="avatar_with_bubble.png"
            ... )
        """
        
        # Load image
        image = Image.open(image_path).convert("RGBA")
        img_width, img_height = image.size
        
        # Use default style if not provided
        if style is None:
            style = SpeechBubbleStyle()
        
        # Wrap text
        wrapped_text = ImageWithSpeechBubble._wrap_text(text, max_chars=30)
        
        # Load font
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                # Try common system fonts
                font_candidates = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "C:\\Windows\\Fonts\\arial.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                ]
                font = None
                for candidate in font_candidates:
                    if os.path.exists(candidate):
                        font = ImageFont.truetype(candidate, font_size)
                        break
                
                if font is None:
                    font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
        
        # Calculate bubble dimensions
        text_bbox = font.getbbox(wrapped_text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        bubble_width = int(img_width * bubble_width_ratio)
        bubble_height = text_height + (2 * style.padding)
        
        # Center horizontally
        bubble_x1 = (img_width - bubble_width) // 2
        bubble_x2 = bubble_x1 + bubble_width
        
        # Position vertically
        if bubble_position == "top":
            bubble_y1 = 20
            bubble_y2 = bubble_y1 + bubble_height
            style.tail_position = "bottom-left"
        else:  # bottom
            bubble_y2 = img_height - 20
            bubble_y1 = bubble_y2 - bubble_height
            style.tail_position = "top-left"
        
        # Draw bubble
        image = ImageWithSpeechBubble._draw_speech_bubble(
            image,
            (bubble_x1, bubble_y1, bubble_x2, bubble_y2),
            wrapped_text,
            style,
            font
        )
        
        # Convert back to RGB if needed
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        
        # Save if output path provided
        if output_path:
            image.save(output_path, quality=95)
            print(f"✓ Image saved to {output_path}")
        
        return image
    
    @staticmethod
    def add_speech_bubble_from_image(
        image: Image.Image,
        text: str,
        style: Optional[SpeechBubbleStyle] = None,
        bubble_position: str = "top",
        bubble_width_ratio: float = 0.8,
        font_size: int = 20,
        font_path: Optional[str] = None
    ) -> Image.Image:
        """
        Add a speech bubble with text to a PIL Image object
        
        Args:
            image: PIL Image object (RGB or RGBA)
            text: Text to display in the bubble
            style: SpeechBubbleStyle configuration (uses default if None)
            bubble_position: "top" or "bottom" position of the bubble
            bubble_width_ratio: Width of bubble as ratio of image (0.0-1.0)
            font_size: Size of the font
            font_path: Path to TrueType font file (uses default if None)
        
        Returns:
            Image object with speech bubble
        """
        
        # Convert to RGBA if needed
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        
        img_width, img_height = image.size
        
        # Use default style if not provided
        if style is None:
            style = SpeechBubbleStyle()
        
        # Wrap text
        wrapped_text = ImageWithSpeechBubble._wrap_text(text, max_chars=30)
        
        # Load font
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                # Try common system fonts
                font_candidates = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "C:\\Windows\\Fonts\\arial.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                ]
                font = None
                for candidate in font_candidates:
                    if os.path.exists(candidate):
                        font = ImageFont.truetype(candidate, font_size)
                        break
                
                if font is None:
                    font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
        
        # Calculate bubble dimensions
        text_bbox = font.getbbox(wrapped_text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        bubble_width = int(img_width * bubble_width_ratio)
        bubble_height = text_height + (2 * style.padding)
        
        # Center horizontally
        bubble_x1 = (img_width - bubble_width) // 2
        bubble_x2 = bubble_x1 + bubble_width
        
        # Position vertically
        if bubble_position == "top":
            bubble_y1 = 20
            bubble_y2 = bubble_y1 + bubble_height
            style.tail_position = "bottom-left"
        else:  # bottom
            bubble_y2 = img_height - 20
            bubble_y1 = bubble_y2 - bubble_height
            style.tail_position = "top-left"
        
        # Draw bubble
        image = ImageWithSpeechBubble._draw_speech_bubble(
            image,
            (bubble_x1, bubble_y1, bubble_x2, bubble_y2),
            wrapped_text,
            style,
            font
        )
        
        # Convert back to RGB if needed for PNG/JPG export
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        
        return image


def add_speech_bubble(
    image_path: str,
    text: str,
    output_path: Optional[str] = None,
    bubble_position: str = "top",
    font_size: int = 20
) -> Image.Image:
    """
    Convenience function to add speech bubble to image
    
    Args:
        image_path: Path to base image
        text: Text for the speech bubble
        output_path: Path to save result (optional)
        bubble_position: "top" or "bottom"
        font_size: Font size in pixels
    
    Returns:
        Image with speech bubble
        
    Example:
        >>> img = add_speech_bubble("avatar.png", "Hola!")
        >>> img.save("avatar_speaking.png")
    """
    return ImageWithSpeechBubble.add_speech_bubble(
        image_path,
        text,
        output_path,
        bubble_position=bubble_position,
        font_size=font_size
    )
