"""Core watermarking logic for MajiMarker."""

import math
from datetime import datetime
from enum import Enum
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class WatermarkPosition(Enum):
    """Vertical position for horizontal watermarks."""
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


class WatermarkOrientation(Enum):
    """Watermark orientation options."""
    HORIZONTAL = "horizontal"
    DIAGONAL_BL_TR = "diagonal_bl_tr"  # Bottom-left to top-right
    DIAGONAL_TL_BR = "diagonal_tl_br"  # Top-left to bottom-right


def get_system_font(size: int) -> ImageFont.FreeTypeFont:
    """Get a system font, falling back to default if not found."""
    font_candidates = [
        "arial.ttf",
        "Arial.ttf",
        "segoeui.ttf",
        "calibri.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]

    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except (OSError, IOError):
            continue

    # Fallback to default
    return ImageFont.load_default()


def calculate_font_size(
    image_width: int,
    image_height: int,
    text: str,
    orientation: WatermarkOrientation = WatermarkOrientation.DIAGONAL_BL_TR,
    stretch: bool = False,
    padding_percent: float = 0.05
) -> int:
    """Calculate optimal font size based on image dimensions and orientation.

    Args:
        image_width: Width of the image
        image_height: Height of the image
        text: Watermark text
        orientation: Watermark orientation
        stretch: If True, stretch text to span edge-to-edge (with padding)
        padding_percent: Padding as percentage of dimension (default 5%)
    """
    if stretch:
        # Stretch mode: span almost full width/diagonal with padding
        padding_factor = 1.0 - (padding_percent * 2)  # padding on both sides

        if orientation == WatermarkOrientation.HORIZONTAL:
            target_width = image_width * padding_factor
        else:
            diagonal = math.sqrt(image_width ** 2 + image_height ** 2)
            target_width = diagonal * padding_factor
    else:
        # Normal mode: use smaller percentage
        if orientation == WatermarkOrientation.HORIZONTAL:
            target_width = image_width * 0.70
        else:
            diagonal = math.sqrt(image_width ** 2 + image_height ** 2)
            target_width = diagonal * 0.55

    # Estimate: each character is roughly 0.6x font size in width
    estimated_size = int(target_width / (len(text) * 0.6))
    # Clamp between reasonable bounds
    return max(20, min(estimated_size, 300))


def _resolve_output_path(base: Path) -> Path:
    """Return base if it doesn't exist; otherwise append _2, _3, … until a free slot is found."""
    if not base.exists():
        return base
    stem, suffix, parent = base.stem, base.suffix, base.parent
    for i in range(2, 1000):
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Too many existing variants of {base}")


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c * 2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def add_watermark(
    image_path: str | Path,
    purpose: str,
    opacity: int = 40,
    font_size: int | None = None,
    date_format: str = "%d/%m/%Y",
    output_path: str | Path | None = None,
    orientation: WatermarkOrientation = WatermarkOrientation.DIAGONAL_BL_TR,
    position: WatermarkPosition = WatermarkPosition.MIDDLE,
    stretch: bool = False,
    color: tuple[int, int, int] = (128, 128, 128)
) -> Path:
    """
    Add watermark text to an image.

    Args:
        image_path: Path to the input image
        purpose: Purpose/keperluan text for watermark
        opacity: 0–255 alpha value; callers should convert from percent via int(round(pct * 2.55))
        font_size: Font size (auto-calculated if None)
        date_format: Date format string
        output_path: Output path; if None, auto-generated with _resolve_output_path (never overwrites). If provided, overwrites unconditionally.
        orientation: Watermark orientation (horizontal or diagonal)
        position: Vertical position for horizontal watermarks (top/middle/bottom)
        stretch: If True, stretch text to span edge-to-edge (with padding)
        color: RGB tuple for watermark color (default gray)

    Returns:
        Path to the watermarked image
    """
    image_path = Path(image_path)

    # Generate output path if not provided; auto-increment to avoid silent overwrites
    if output_path is None:
        base = image_path.parent / f"{image_path.stem}_watermarked{image_path.suffix}"
        output_path = _resolve_output_path(base)
    else:
        output_path = Path(output_path)

    # Open and convert image to RGBA for transparency support
    with Image.open(image_path) as img:
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        width, height = img.size

        # Build watermark text
        date_str = datetime.now().strftime(date_format)
        watermark_text = f"{purpose} - {date_str}"

        # Calculate font size if not provided
        if font_size is None:
            font_size = calculate_font_size(width, height, watermark_text, orientation, stretch)

        font = get_system_font(font_size)

        # Create transparent overlay for watermark
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # Get text bounding box
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Color with specified opacity
        text_color = (color[0], color[1], color[2], opacity)

        if orientation == WatermarkOrientation.HORIZONTAL:
            # Horizontal watermark with position
            txt_layer = _create_horizontal_watermark(
                width, height, watermark_text, font, text_color,
                text_width, text_height, position
            )
        else:
            # Diagonal watermark
            txt_layer = _create_diagonal_watermark(
                width, height, watermark_text, font, text_color,
                text_width, text_height, orientation
            )

        # Composite the watermark onto the image
        watermarked = Image.alpha_composite(img, txt_layer)

        # Convert back to RGB if original was not RGBA (for JPEG compatibility)
        if image_path.suffix.lower() in ['.jpg', '.jpeg']:
            watermarked = watermarked.convert('RGB')

        # Save with high quality
        save_kwargs = {}
        if image_path.suffix.lower() in ['.jpg', '.jpeg']:
            save_kwargs['quality'] = 95
        elif image_path.suffix.lower() == '.png':
            save_kwargs['compress_level'] = 6

        watermarked.save(output_path, **save_kwargs)

    return output_path


def _create_horizontal_watermark(
    width: int,
    height: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    color: tuple,
    text_width: int,
    text_height: int,
    position: WatermarkPosition
) -> Image.Image:
    """Create a horizontal watermark layer."""
    txt_layer = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    txt_draw = ImageDraw.Draw(txt_layer)

    # Center horizontally
    text_x = (width - text_width) // 2

    # Position vertically based on option
    margin = int(height * 0.05)  # 5% margin from edges

    if position == WatermarkPosition.TOP:
        text_y = margin
    elif position == WatermarkPosition.BOTTOM:
        text_y = height - text_height - margin
    else:  # MIDDLE
        text_y = (height - text_height) // 2

    txt_draw.text((text_x, text_y), text, font=font, fill=color)
    return txt_layer


def _create_diagonal_watermark(
    width: int,
    height: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    color: tuple,
    text_width: int,
    text_height: int,
    orientation: WatermarkOrientation
) -> Image.Image:
    """Create a diagonal watermark layer."""
    # Calculate diagonal angle
    base_angle = math.degrees(math.atan2(height, width))

    if orientation == WatermarkOrientation.DIAGONAL_BL_TR:
        # Bottom-left to top-right (positive angle)
        angle = base_angle
    else:
        # Top-left to bottom-right (negative angle)
        angle = -base_angle

    # Create a larger canvas for the rotated text
    diagonal = int(math.sqrt(width ** 2 + height ** 2))
    txt_layer = Image.new('RGBA', (diagonal * 2, diagonal * 2), (255, 255, 255, 0))
    txt_draw = ImageDraw.Draw(txt_layer)

    # Draw text at center of the larger canvas
    text_x = (diagonal * 2 - text_width) // 2
    text_y = (diagonal * 2 - text_height) // 2

    txt_draw.text((text_x, text_y), text, font=font, fill=color)

    # Rotate the text layer
    txt_layer = txt_layer.rotate(angle, resample=Image.BICUBIC, expand=False)

    # Crop to original image size from center
    crop_x = (txt_layer.width - width) // 2
    crop_y = (txt_layer.height - height) // 2
    txt_layer = txt_layer.crop((crop_x, crop_y, crop_x + width, crop_y + height))

    return txt_layer


def process_batch(
    image_paths: list[str | Path],
    purpose: str,
    opacity: int = 40,
    output_folder: Path | None = None,
    orientation: WatermarkOrientation = WatermarkOrientation.DIAGONAL_BL_TR,
    position: WatermarkPosition = WatermarkPosition.MIDDLE,
    stretch: bool = False,
    color: tuple[int, int, int] = (128, 128, 128),
    progress_callback=None
) -> list[Path]:
    """
    Process multiple images with the same watermark.

    Args:
        image_paths: List of image paths to process
        purpose: Purpose text for watermark
        opacity: Opacity value 0-255
        output_folder: Optional folder for output files
        orientation: Watermark orientation
        position: Vertical position for horizontal watermarks
        stretch: If True, stretch text to span edge-to-edge
        color: RGB tuple for watermark color
        progress_callback: Optional callback(current, total) for progress updates

    Returns:
        List of output paths
    """
    results = []
    total = len(image_paths)

    for i, image_path in enumerate(image_paths):
        image_path = Path(image_path)

        if output_folder:
            output_path = output_folder / f"{image_path.stem}_watermarked{image_path.suffix}"
        else:
            output_path = None

        result = add_watermark(
            image_path, purpose, opacity,
            output_path=output_path,
            orientation=orientation,
            position=position,
            stretch=stretch,
            color=color
        )
        results.append(result)

        if progress_callback:
            progress_callback(i + 1, total)

    return results
