import os
import cv2
import numpy as np
import random

def generate_checkerboard_with_oval_mask(output_dir, num_versions_per_ratio=10):
    """
    Generate black/white checkerboards with oval masks and save to specified directory.
    
    Args:
        output_dir (str): Directory to save output images
        num_versions_per_ratio (int): Number of versions to generate per black ratio
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define constants
    TILE_SIZE = 32
    BOARD_WIDTH_TILES = 9
    BOARD_HEIGHT_TILES = 11
    LINE_WIDTH = 3
    CHECKERBOARD_WIDTH = BOARD_WIDTH_TILES * TILE_SIZE + (BOARD_WIDTH_TILES - 1) * LINE_WIDTH
    CHECKERBOARD_HEIGHT = BOARD_HEIGHT_TILES * TILE_SIZE + (BOARD_HEIGHT_TILES - 1) * LINE_WIDTH
    TARGET_SIZE = 512
    
    # Medium gray color for lines and padding
    MEDIUM_GRAY = 127
    
    # Generate different black/white ratios (21% to 81% black, in 3% increments)
    black_ratios = [i/100 for i in range(21, 82, 3)]
    
    image_counter = 0
    
    # Generate multiple images with different black ratios
    for ratio_idx, black_ratio in enumerate(black_ratios):
        print(f"Generating {num_versions_per_ratio} versions with {int(black_ratio*100)}% black tiles...")
        
        # Generate multiple versions for each ratio
        for version in range(num_versions_per_ratio):
            # Generate checkerboard pattern with unique random seed for each version
            checkerboard = generate_random_checkerboard(BOARD_WIDTH_TILES, BOARD_HEIGHT_TILES, TILE_SIZE, black_ratio, version)
            
            # Apply oval mask
            #masked_checkerboard = apply_oval_mask(checkerboard, CHECKERBOARD_WIDTH, CHECKERBOARD_HEIGHT)
            masked_checkerboard = apply_aperture_mask(checkerboard, CHECKERBOARD_WIDTH, CHECKERBOARD_HEIGHT)

            # Resize to target size with padding
            #final_image = masked_checkerboard
            final_image = resize_with_padding(masked_checkerboard, TARGET_SIZE, MEDIUM_GRAY)
            
            # Save image
            output_path = os.path.join(output_dir, f"checkerboard_{ratio_idx+1:02d}_{int(black_ratio*100):02d}_{version+1:02d}.png")
            cv2.imwrite(output_path, final_image)
            image_counter += 1
            
            if (version + 1) % 5 == 0:
                print(f"  Generated {version + 1}/{num_versions_per_ratio} versions for {int(black_ratio*100)}% ratio")
    
    print(f"Generated {image_counter} total checkerboard images")
    print(f"Generated {len(black_ratios)} different black ratios with {num_versions_per_ratio} versions each")

def generate_random_checkerboard(width_tiles, height_tiles, TILE_SIZE, black_ratio, version_seed=None):
    """
    Generate a checkerboard with random placement of black and white tiles.
    
    Args:
        width_tiles (int): Number of tiles horizontally
        height_tiles (int): Number of tiles vertically
        black_ratio (float): Proportion of black tiles (0.0 to 1.0)
        version_seed (int): Seed for random number generator to ensure different patterns
    
    Returns:
        numpy.ndarray: Generated checkerboard image
    """
    LINE_WIDTH = 3
    MEDIUM_GRAY = 127
    LINES_GRAY = 165
    
    # Calculate total dimensions including lines
    total_width = width_tiles * TILE_SIZE + (width_tiles - 1) * LINE_WIDTH
    total_height = height_tiles * TILE_SIZE + (height_tiles - 1) * LINE_WIDTH
    
    # Create blank image (white background)
    img = np.ones((total_height, total_width), dtype=np.uint8) * 255
    
    # Total number of tiles
    total_tiles = width_tiles * height_tiles
    
    # Calculate number of black tiles
    black_tiles = int(total_tiles * black_ratio)
    
    # Create list of tile positions
    tile_positions = [(i, j) for i in range(width_tiles) for j in range(height_tiles)]
    
    # Set random seed based on version to ensure different patterns
    if version_seed is not None:
        random.seed(version_seed)
    
    # Randomly select positions for black tiles
    black_positions = random.sample(tile_positions, black_tiles)
    
    # Draw tiles
    for i in range(width_tiles):
        for j in range(height_tiles):
            # Calculate position
            x_start = i * (TILE_SIZE + LINE_WIDTH)
            y_start = j * (TILE_SIZE + LINE_WIDTH)
            
            # Draw tile
            if (i, j) in black_positions:
                # Black tile
                img[y_start:y_start+TILE_SIZE, x_start:x_start+TILE_SIZE] = 50
            else:
                # White tile
                img[y_start:y_start+TILE_SIZE, x_start:x_start+TILE_SIZE] = 205
    
    # Add medium gray lines between tiles
    # Vertical lines
    for i in range(1, width_tiles):
        x_pos = i * TILE_SIZE + (i - 1) * LINE_WIDTH
        img[:, x_pos:x_pos+LINE_WIDTH] = LINES_GRAY
    
    # Horizontal lines
    for j in range(1, height_tiles):
        y_pos = j * TILE_SIZE + (j - 1) * LINE_WIDTH
        img[y_pos:y_pos+LINE_WIDTH, :] = LINES_GRAY
    
    return img

def apply_aperture_mask(img, width, height, feather=0.01, bg=127):
    """
    Soft inverse-egg aperture mask (wider at top, narrower at bottom)
    using a Gaussian edge falloff (no rectangular artifacts).
    """

    y, x = np.ogrid[:height, :width]
    cx, cy = width / 2, height / 2

    # Base radii
    ry = (height - 10) / 2
    rx_base = (width - 10) / 2

    # Normalized vertical coordinate
    y_norm = (y - cy) / ry

    shape_strength = 0.1
    rx = rx_base * (1 - shape_strength * y_norm)
    rx = np.clip(rx, rx_base * 0.5, rx_base * 1.5)

    # Elliptical distance field
    dist = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)

    # ---- Gaussian falloff based on distance ----
    # dist = 1 at the aperture boundary
    edge_dist = dist - 1.0

    # Convert feather to sigma in normalized space
    sigma = feather

    # Gaussian falloff (inside stays ~1, outside decays smoothly)
    mask = np.exp(-(edge_dist ** 2) / (2 * sigma ** 2))

    # Clamp inside aperture to 1
    mask[dist <= 1] = 1.0

    img_f = img.astype(np.float32)
    result = img_f * mask + bg * (1 - mask)

    return result.astype(np.uint8)

def resize_with_padding(image, target_size = 512, pad_color=127):
    """
    1. Resize image to 300x350 (width x height)
    2. Place it on a 512x512 background
    3. Center horizontally
    4. Align top at 3/4 of image height
    """

    new_w, new_h = 275, 330  # required resize dimensions

    # Resize image first
    resized_img = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Create 512x512 padded background
    padded_img = np.ones((target_size, target_size), dtype=np.uint8) * pad_color

    # Center horizontally
    start_x = (target_size - new_w) // 2

    # Align top at specified height percentage
    start_y = int(target_size * 0.25)

    # Prevent overflow at bottom
    if start_y + new_h > target_size:
        start_y = target_size - new_h

    # Place resized image
    padded_img[start_y:start_y+new_h, start_x:start_x+new_w] = resized_img

    return padded_img

# Example usage
if __name__ == "__main__":
    # Set your output directory here
    OUTPUT_DIRECTORY = "Path/out"  # Change this to your desired output directory
    
    # Generate checkerboard images (10 versions per ratio)
    generate_checkerboard_with_oval_mask(OUTPUT_DIRECTORY, num_versions_per_ratio=10)