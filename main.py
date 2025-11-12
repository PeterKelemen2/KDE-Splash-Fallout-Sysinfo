import os
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import info
import effects
import gif_config

config = gif_config.Config()


def split_text(text, segment):
    """Incrementally adds parts to the list."""
    part_size = len(text) // segment
    result = []
    for i in range(0, len(text), part_size):
        result.append(text[: i + part_size])  # Just build up text, no cursor yet
    return result


def display_terminal(text):
    """Displays text progressively with a blinking cursor effect in an OpenCV window."""
    # Create a black image to display text
    global config
    font_size = config.FONT_SIZE
    font_path = config.FONT_PATH
    fps = config.FPS
    text_dur = config.DURATION_TEXT
    blink_dur = config.DURATION_CURSOR

    frame_count = fps * text_dur
    frame_time = text_dur / frame_count
    frame_list = []
    current_time = 0.0

    text_list = split_text(text, frame_count)

    width = config.RES_X
    height = config.RES_Y
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Load the font
    try:
        font = ImageFont.truetype(font_path, size=font_size)
    except IOError:
        print("Font not found, using default.")
        font = ImageFont.load_default()

    # Convert image to Pillow format
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)

    font_color_rgb = config.FONT_COLOR
    font_color_bgr = (font_color_rgb[2], font_color_rgb[1], font_color_rgb[0])

    y_position = 50  # Fixed Y position (don't center vertically)
    line_height = font_size * 1.5  # Distance between lines

    first_line_width = draw.textbbox((0, 0), text.split("\n")[0], font=font)[2]
    x_position = (width - first_line_width) // 2

    cv2.imshow("Terminal", image)
    # cv2.moveWindow("Terminal", 1920 + (1920 - width) // 2, 100)

    for i, part in enumerate(text_list):
        # Clear the image
        pil_image.paste((0, 0, 0), [0, 0, width, height])

        # Add blinking cursor every 0.5 seconds and leave if there for 0.5 seconds
        text = part + "█"

        # Split text into lines
        lines = text.split("\n")

        for line in lines:
            # Draw text at (centered X, fixed Y)
            # draw.text((x_position, y_position), line, font=font, fill=font_color)

            effects.apply_glow(
                pil_image,
                line,
                (x_position, y_position),
                font,
                glow_color=(*font_color_bgr, 128),
            )

            y_position += line_height  # Move to next line

        # Convert back to OpenCV format and show
        image = np.array(pil_image)
        warped_image = effects.apply_crt_warp(
            image,
            distortion=config.EFFECT_WARP_INTENSITY
        )
        scanlined_image = effects.apply_scanlines_with_noise(
            warped_image,
            scanline_intensity=config.EFFECT_SCANLINE_INTENSITY,
            noise_intensity=config.EFFECT_NOISE_INTENSITY
        )

        frame_list.append(scanlined_image)
        cv2.imshow("Terminal", scanlined_image)

        current_time = current_time + frame_time

        # Delay for effect
        key = cv2.waitKey(int(frame_time * 1000))
        if key == 27:  # ESC to exit
            break

        # Reset Y position for the next frame
        y_position = 50

    # ========================== BLINKING CURSORS  ==========================
    frame_index = 0  # Initialize frame index for blinking
    aux_frame_index = 0
    cursor_on_dur = 0.5  # Seconds
    on_for_frame = cursor_on_dur / frame_time

    cursor_on = True

    print(f"Cursor on for {on_for_frame} frames")

    while frame_index < fps * blink_dur:
        # Clear the image
        pil_image.paste((0, 0, 0), [0, 0, width, height])

        # Toggle cursor state
        if aux_frame_index > on_for_frame:
            cursor_on = not cursor_on
            aux_frame_index = 0
            print(f"Cursor state: {cursor_on}")

        cursor = "█" if cursor_on else ""

        text = text_list[-1] + cursor  # Use the last printed text

        # Draw text
        lines = text.split("\n")
        for line in lines:
            effects.apply_glow(
                pil_image,
                line,
                (x_position, y_position),
                font,
                glow_color=(*font_color_bgr, 128),
            )
            y_position += line_height

        # Convert back to OpenCV format and show
        image = np.array(pil_image)
        warped_image = effects.apply_crt_warp(
            image,
            distortion=config.EFFECT_WARP_INTENSITY
        )
        scanlined_image = effects.apply_scanlines_with_noise(
            warped_image,
            scanline_intensity=config.EFFECT_SCANLINE_INTENSITY,
            noise_intensity=config.EFFECT_NOISE_INTENSITY
        )

        # Store the frame
        frame_list.append(scanlined_image)
        cv2.imshow("Terminal", scanlined_image)

        # Delay for effect
        key = cv2.waitKey(int(frame_time * 1000))
        if key == 27:  # ESC to exit
            break

        # Increment frame index and reset y_position
        frame_index += 1
        aux_frame_index += 1
        y_position = 50  # Reset Y position

    print("Started saving gif...")
    pil_frames = [Image.fromarray(frame) for frame in frame_list]
    pil_frames[0].save(
        "output.gif",
        save_all=True,
        append_images=pil_frames[1:],
        duration=1000 / fps,  # Frame duration
        loop=0,  # Loop the GIF once
        optimize=True,  # Optimize the image
        quality=50,  # Set quality (lower value = smaller file size, but lower quality)
    )
    print("Saving finished!")


    # Keep window open after completing the text display
    # while True:
    #     key = cv2.waitKey(1)  # Wait for any key press
    #     if key != -1:  # Exit the window on any key press
    #         break

    # Close window
    cv2.destroyAllWindows()


def main():
    global config
    config = gif_config.Config.load_from_json()

    terminal_string = info.create_terminal_string(config)
    print(terminal_string)

    display_terminal(terminal_string)


if __name__ == "__main__":
    main()
