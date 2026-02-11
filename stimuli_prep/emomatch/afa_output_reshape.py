import os
from PIL import Image
import numpy as np

def process_images(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    bg_width, bg_height = 512, 512
    fg_width, fg_height = 369, 512

    # Create gray RGBA background (127 gray, fully opaque)
    background_array = np.full((bg_height, bg_width, 4), (127, 127, 127, 255), dtype=np.uint8)
    background_template = Image.fromarray(background_array, mode="RGBA")

    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".png")]

    for idx, filename in enumerate(sorted(image_files)):
        input_path = os.path.join(input_dir, filename)

        # Open and preserve alpha
        fg_image = Image.open(input_path).convert("RGBA")

        # Resize if needed
        if fg_image.size != (fg_width, fg_height):
            fg_image = fg_image.resize((fg_width, fg_height), Image.LANCZOS)

        background = background_template.copy()

        x_offset = (bg_width - fg_width) // 2
        y_offset = (bg_height - fg_height) // 2

        # Paste using alpha channel as mask
        background.paste(fg_image, (x_offset, y_offset), fg_image)

        output_path = os.path.join(output_dir, filename)
        background.save(output_path)

        print(f"Saved: {output_path}")



if __name__ == "__main__":
    input_directory = "/path/in"
    output_directory = "/path/out"
    process_images(input_directory, output_directory)
