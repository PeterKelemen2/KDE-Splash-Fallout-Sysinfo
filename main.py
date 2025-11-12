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


def get_frame(text, pil_image, x_pos, y_pos, font):
    font_color_bgr = (config.FONT_COLOR[2], config.FONT_COLOR[1], config.FONT_COLOR[0])
    
    lines = text.split("\n")

    for line in lines:
        effects.apply_glow(
            pil_image,
            line,
            (x_pos, y_pos),
            font,
            glow_color=(*font_color_bgr, 128),
        )
        y_pos += config.LINE_SPACE

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

    return scanlined_image


def display_terminal(text):
    """Displays text progressively with a blinking cursor effect in an OpenCV window."""
    global config

    frame_count = config.FPS * config.DURATION_TEXT
    frame_time = config.DURATION_TEXT / frame_count
    frame_list = []
    current_time = 0.0

    text_list = split_text(text, frame_count)

    image = np.zeros((config.RES_Y, config.RES_X, 3), dtype=np.uint8)

    # Load the font
    try:
        font = ImageFont.truetype(config.FONT_PATH, size=config.FONT_SIZE)
    except IOError:
        print("Font not found, using default.")
        font = ImageFont.load_default()

    # Convert image to Pillow format
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)

    y_position = 50  # Fixed Y position (don't center vertically)

    first_line_width = draw.textbbox((0, 0), text.split("\n")[0], font=font)[2]
    x_position = (config.RES_X - first_line_width) // 2

    cv2.imshow("Terminal", image)
    # cv2.moveWindow("Terminal", 1920 + (1920 - width) // 2, 100)

    for i, part in enumerate(text_list):
        # Clear the image
        pil_image.paste((0, 0, 0), [0, 0, config.RES_X, config.RES_Y])

        # Add blinking cursor every 0.5 seconds and leave if there for 0.5 seconds
        text = part + "█"

        new_frame = get_frame(text, pil_image, x_position, y_position, font)
        frame_list.append(new_frame)
        cv2.imshow("Terminal", new_frame)

        current_time = current_time + frame_time

        # Delay for effect
        key = cv2.waitKey(int(frame_time * 1000))
        if key == 27:  # ESC to exit
            break

        # Reset Y position for the next frame
        y_position = 50

    # ========================== BLINKING CURSOR  ==========================
    frame_index = 0  # Initialize frame index for blinking
    aux_frame_index = 0
    cursor_on_dur = 0.5  # Seconds
    on_for_frame = cursor_on_dur / frame_time

    cursor_on = True

    print(f"Cursor on for {on_for_frame} frames")

    while frame_index < config.FPS * config.DURATION_CURSOR:
        # Clear the image
        pil_image.paste((0, 0, 0), [0, 0, config.RES_X, config.RES_Y])

        # Toggle cursor state
        if aux_frame_index > on_for_frame:
            cursor_on = not cursor_on
            aux_frame_index = 0
            print(f"Cursor state: {cursor_on}")

        cursor = "█" if cursor_on else ""

        text = text_list[-1] + cursor  # Use the last printed text

        new_frame = get_frame(text, pil_image, x_position, y_position, font)
        frame_list.append(new_frame)
        cv2.imshow("Terminal", new_frame)

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
        duration=1000 / config.FPS,  # Frame duration
        loop=0,  # Loop the GIF once
        optimize=True,
        quality=config.GIF_QUALITY, 
    )
    print("Saving finished!")

    cv2.destroyAllWindows()


def main():
    global config
    config = gif_config.Config.load_from_json()

    terminal_string = info.create_terminal_string(config)
    print(terminal_string)

    display_terminal(terminal_string)


if __name__ == "__main__":
    main()
