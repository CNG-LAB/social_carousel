# This was heavily vibe coded with ChatGPT
# This script handles the display for setting landmarks

import cv2
import pandas as pd
import glob
import os

# Set parameters
def set_params():
    LEFT_EYE_IDX = 0
    RIGHT_EYE_IDX = 1
    eye_y_ratio = 0.5
    OUTPUT_SIZE = (562, 762)
    DESIRED_EYE_DISTANCE = 120.0  # pixels

    return LEFT_EYE_IDX, RIGHT_EYE_IDX, eye_y_ratio, DESIRED_EYE_DISTANCE, OUTPUT_SIZE

# Set directories
def set_dirs():
    image_dir = "/data/tu_royer_private/emomatch_orig/original/"
    os.makedirs(image_dir, exist_ok=True)

    landmarks_dir = "/data/tu_royer_private/emomatch_orig/aligned/"
    os.makedirs(landmarks_dir, exist_ok=True)

    output_dir = "/data/tu_royer_private/emomatch_orig/aligned/"
    os.makedirs(output_dir, exist_ok=True)

    return image_dir, landmarks_dir, output_dir

# list all files in a directory with a specified extension
def list_files_df(directory_path, extension):
    """
    Returns a pandas DataFrame containing the names of all .jpg files
    in the specified directory.
    """
    jpg_files = [
        file for file in os.listdir(directory_path)
        if file.lower().endswith(extension) and os.path.isfile(os.path.join(directory_path, file))
    ]
    df = pd.DataFrame(jpg_files, columns=["filename"])
    return df
