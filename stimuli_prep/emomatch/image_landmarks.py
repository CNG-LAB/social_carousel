# This was heavily vibe coded with ChatGPT
# This script outputs a list of landmark coordinates for each image in your specified directory

# The interface is handled by set_landmarks.py
# Commands:
#    - Left click: add landmark
#    - u: undo last point
#    - r: reset all points
#    - s: save & continue to next image
#    - q: quit without saving

# Order of landmark placement should always be the same. For carousel-emomatch, we use 6 points: 
#    pupil left eye
#    pupil right eye
#    tip of nose
#    left mouth corner
#    middle of mouth
#    right mouth corner

# Note: This runs the whole image set one shot so plan accordingly :)
#       If you want to set your landmarks in multiple runs, a hacky solution
#       could be to split your original image set in different directories, and 
#       call this script once for each directory. Keep the output location identical
#       across runs.

import os
import numpy as np
import pandas as pd
from set_landmarks import main as pick_landmarks
from align_utilities import list_files_df 

# Set directories
image_dir, landmarks_dir, output_dir = set_dirs()

# make a list of image files
face_list = list_files_df(image_dir, ".jpg")

# run the landmark placement
for idx, row in face_list.iterrows():
    image_name = row["filename"]
    image_path = os.path.join(image_dir, image_name)

    print(f"\nProcessing {image_name} ({idx + 1}/{len(face_list)})")

    landmarks = pick_landmarks(image_path)

    if not landmarks:
        print("No landmarks saved, skipping.")
        continue

    landmarks_array = np.array(landmarks)

    output_path = os.path.join(
        output_dir,
        os.path.splitext(image_name)[0] + "_landmarks.txt"
    )

    np.savetxt(output_path, landmarks_array, fmt="%d")

    print(f"Saved landmarks to {output_path}")

