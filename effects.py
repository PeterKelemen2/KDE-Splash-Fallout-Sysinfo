import cv2
import numpy as np
from gif_config import NoiseType
from PIL import Image, ImageDraw, ImageFilter


def apply_crt_warp(image, distortion=0.15):
    """Applies a CRT-style screen warp with subtle barrel distortion."""
    height, width = image.shape[:2]

    # Create normalized coordinate grid (-1 to 1)
    y, x = np.indices((height, width), dtype=np.float32)
    x = (x - width / 2) / (width / 2)
    y = (y - height / 2) / (height / 2)

    # Compute radial distance
    r = np.sqrt(x**2 + y**2)

    # Apply barrel distortion formula
    factor = 1 + distortion * (r**2)

    # Transform coordinates
    new_x = (x * factor) * (width / 2) + width / 2
    new_y = (y * factor) * (height / 2) + height / 2

    # Ensure new coordinates are within bounds
    new_x = np.clip(new_x, 0, width - 1)
    new_y = np.clip(new_y, 0, height - 1)

    # Remap image using OpenCV
    crt_warped = cv2.remap(
        image,
        new_x.astype(np.float32),
        new_y.astype(np.float32),
        interpolation=cv2.INTER_LINEAR,
    )

    return crt_warped


def apply_scanlines(image, intensity=0.3):
    """Applies a CRT-style scanline effect."""
    height, width = image.shape[:2]

    # Create a scanline pattern (alternating dark lines)
    scanline = np.ones((height, width, 3), dtype=np.float32)
    scanline[::2] *= 1 - intensity  # Darken every other row

    # Apply scanlines to the image
    image = image.astype(np.float32) / 255.0  # Normalize image for blending
    scanline_effect = (image * scanline) * 255.0
    return scanline_effect.astype(np.uint8)


def apply_scanlines_with_noise(image, scanline_intensity=0.3, noise_intensity=0.03, noise_scale=2.5, noise_type = NoiseType.MONOCHROME):
    """
    Applies CRT-style scanlines with noise to an image.

    noise_scale: larger values = bigger noise particles, can be float
    """
    height, width = image.shape[:2]

    # Create a scanline pattern (alternating dark lines)
    scanline = np.ones((height, width, 3), dtype=np.float32)
    scanline[::2] *= 1 - scanline_intensity  # Darken every other row

    # Generate low-res noise
    small_h = max(1, int(round(height / noise_scale)))
    small_w = max(1, int(round(width / noise_scale)))
    
    if noise_type == NoiseType.COLOR:
        noise_small = np.random.normal(0, noise_intensity, (small_h, small_w, 3)).astype(np.float32)
    elif noise_type == NoiseType.MONOCHROME:
        # Single channel noise, then broadcast to RGB
        mono_noise = np.random.normal(0, noise_intensity, (small_h, small_w, 1)).astype(np.float32)
        noise_small = np.repeat(mono_noise, 3, axis=2)
    else:
        raise ValueError(f"Unknown noise_type: {noise_type}")

    # Upscale noise to full image size
    noise = cv2.resize(noise_small, (width, height), interpolation=cv2.INTER_NEAREST)

    # Normalize image for blending
    image = image.astype(np.float32) / 255.0

    # Apply scanline effect
    scanline_effect = image * scanline

    # Apply noise
    noisy_image = np.clip(scanline_effect + noise, 0, 1)

    return (noisy_image * 255).astype(np.uint8)


def apply_glow(draw_image, text, position, font, glow_color=(0, 255, 0, 128), intensity=3):
    """Draws glowing text by layering blurred text."""
    x, y = position

    # Create a temporary transparent image to draw blurred text
    temp_img = Image.new("RGBA", draw_image.size, (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)

    # Draw multiple blurred layers to simulate glow
    for offset in range(1, intensity + 1):
        temp_draw.text((x - offset, y), text, font=font, fill=glow_color)
        temp_draw.text((x + offset, y), text, font=font, fill=glow_color)
        temp_draw.text((x, y - offset), text, font=font, fill=glow_color)
        temp_draw.text((x, y + offset), text, font=font, fill=glow_color)

    # Apply blur to the temporary image
    temp_img = temp_img.filter(ImageFilter.GaussianBlur(radius=2))

    # Paste the blurred glow onto the main image using alpha mask
    draw_image.paste(temp_img, (0, 0), temp_img.split()[3])

    # Draw the original text on top
    draw = ImageDraw.Draw(draw_image)  # Redraw the original text
    draw.text((x, y), text, font=font, fill=glow_color[:3])  # Drop alpha for main text

