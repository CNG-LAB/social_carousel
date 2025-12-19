# This was heavily vibe coded with ChatGPT
# This script applies the affine tranformation and outputs the aligned image

# Note: Your images should be already somewhat in the same configuation/size.
# if there is too much variance across faces, the alignment will likely fail 
# or give some werid results as we align to the average landmark coordinate 
# of the set (there is no normalization or rescaling)... 
# We are open to enhacements though - open a pull request :)

import cv2
import numpy as np
import glob
import os
from align_utilities import list_files_df, set_dirs, set_params


def load_landmark_files(landmark_dir, ext="txt"):
    files = sorted(glob.glob(os.path.join(landmark_dir, f"*.{ext}")))
    if not files:
        raise ValueError("No landmark files found.")

    landmarks = []
    for f in files:
        pts = np.loadtxt(f, dtype=np.float32)
        if pts.ndim == 1:
            pts = pts.reshape(-1, 2)
        landmarks.append(pts)

    return np.stack(landmarks, axis=0)  # (N, L, 2)


def normalize_landmarks(
    landmarks,
    left_eye_idx,
    right_eye_idx
):
    """
    Centers, rotates, and scales landmarks using eye positions.

    Args:
        landmarks (np.ndarray): (N, L, 2)
        left_eye_idx (int)
        right_eye_idx (int)

    Returns:
        normalized (np.ndarray): (N, L, 2)
    """

    normalized = []

    for pts in landmarks:
        # 1. Center landmarks
        center = np.mean(pts, axis=0)
        pts_centered = pts - center

        # 2. Compute eye vector
        left_eye = pts_centered[left_eye_idx]
        right_eye = pts_centered[right_eye_idx]

        eye_vec = right_eye - left_eye
        eye_dist = np.linalg.norm(eye_vec)

        if eye_dist < 1e-6:
            raise ValueError("Invalid eye distance.")

        # 3. Compute rotation angle (to horizontal)
        angle = np.arctan2(eye_vec[1], eye_vec[0])

        # Rotation matrix to align eyes horizontally
        cos_a = np.cos(-angle)
        sin_a = np.sin(-angle)
        R = np.array([
            [cos_a, -sin_a],
            [sin_a,  cos_a]
        ], dtype=np.float32)

        # 4. Rotate landmarks
        pts_rotated = pts_centered @ R.T

        # 5. Scale to unit eye distance
        pts_scaled = pts_rotated / eye_dist

        normalized.append(pts_scaled)

    return np.stack(normalized, axis=0)


def compute_canonical_landmarks(normalized_landmarks):
    """
    Computes mean landmark configuration.

    Args:
        normalized_landmarks (np.ndarray): (N, L, 2)

    Returns:
        canonical (np.ndarray): (L, 2)
    """
    return np.mean(normalized_landmarks, axis=0)


def fit_canonical_to_frame(
    canonical_landmarks,
    output_size,
    scale_factor=0.9
):
    """
    Fits canonical landmarks into image frame using all points.

    Args:
        canonical_landmarks (np.ndarray): (L, 2), normalized
        output_size (tuple): (W, H)
        scale_factor (float): fraction of frame to occupy

    Returns:
        fitted (np.ndarray): (L, 2)
    """

    # Normalize canonical to unit RMS distance
    centered = canonical_landmarks - np.mean(canonical_landmarks, axis=0)
    rms = np.sqrt(np.mean(np.sum(centered ** 2, axis=1)))
    centered /= rms

    # Scale to image
    scale = scale_factor * min(output_size)
    scaled = centered * scale

    # Center in image
    img_center = np.array([output_size[0] / 2, output_size[1] / 2])
    fitted = scaled + img_center

    return fitted


def rescale_canonical_landmarks(
    canonical_landmarks,
    output_size,
    desired_eye_distance,
    left_eye_idx,
    right_eye_idx,
    eye_y_ratio
):
    """
    Scales canonical landmarks to desired image size.

    Args:
        canonical_landmarks (np.ndarray): (L, 2)
        output_size (tuple): (width, height)
        desired_eye_distance (float)
        left_eye_idx (int)
        right_eye_idx (int)
        eye_y_ratio (float) - play with this value if faces a cropped vertically

    Returns:
        scaled_landmarks (np.ndarray): (L, 2)
    """

    # Scale
    le = canonical_landmarks[left_eye_idx]
    re = canonical_landmarks[right_eye_idx]
    current_dist = np.linalg.norm(le - re)
    scale = desired_eye_distance / current_dist
    scaled = canonical_landmarks * scale

    # Eye midpoint
    eye_center = 0.5 * (scaled[left_eye_idx] + scaled[right_eye_idx])

    # Desired eye position
    desired_eye_pos = np.array([
        output_size[0] / 2,               # center horizontally
        output_size[1] * eye_y_ratio      # higher vertically
    ])

    # Translate
    scaled += desired_eye_pos - eye_center
    return scaled


def procrustes_similarity_transform(src, dst):
    """
    Computes similarity transform (sR + t) that maps src → dst
    using all landmark points (least squares).

    Args:
        src (np.ndarray): (L, 2) source landmarks
        dst (np.ndarray): (L, 2) destination landmarks

    Returns:
        M (np.ndarray): 2x3 affine matrix
    """

    src = src.astype(np.float64)
    dst = dst.astype(np.float64)

    # 1. Compute centroids
    src_mean = np.mean(src, axis=0)
    dst_mean = np.mean(dst, axis=0)

    src_centered = src - src_mean
    dst_centered = dst - dst_mean

    # 2. Compute covariance matrix
    H = src_centered.T @ dst_centered

    # 3. SVD
    U, S, Vt = np.linalg.svd(H)

    # 4. Rotation
    R = Vt.T @ U.T

    # Enforce proper rotation (no reflection)
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T

    # 5. Scale
    scale = np.trace(R @ H) / np.sum(src_centered ** 2)

    # 6. Translation
    t = dst_mean - scale * (R @ src_mean)

    # 7. Affine matrix
    M = np.zeros((2, 3))
    M[:, :2] = scale * R
    M[:, 2] = t

    return M


def align_face_image(
    image_path,
    input_landmarks,
    canonical_landmarks,
    output_size,
    output_path
):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not load image.")

    src = np.asarray(input_landmarks, dtype=np.float32)
    dst = np.asarray(canonical_landmarks, dtype=np.float32)

    M = procrustes_similarity_transform(src, dst)

    aligned = cv2.warpAffine(
        img,
        M,
        output_size,
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101
    )

    input_basename = os.path.splitext(os.path.basename(input_image_path))[0]
    input_basename_ext = input_basename + "_align.png"
    output_path = os.path.join(output_dir, input_basename_ext)
    cv2.imwrite(output_path, aligned)
    return aligned


######### Pipeline parameters #########

# Set directories
image_dir, landmarks_dir, output_dir = set_dirs()

# Set free parameters 
LEFT_EYE_IDX, RIGHT_EYE_IDX, eye_y_ratio, DESIRED_EYE_DISTANCE, OUTPUT_SIZE = set_params()


######### build canonical #########
# Load landmarks
all_landmarks = load_landmark_files(landmarks_dir)
nFaces = all_landmarks.shape[0]

# Normalize
normalized = normalize_landmarks(
    all_landmarks,
    LEFT_EYE_IDX,
    RIGHT_EYE_IDX
)

# Average
canonical = compute_canonical_landmarks(normalized)

# Rescale
canonical_rescaled = rescale_canonical_landmarks(
    canonical,
    OUTPUT_SIZE,
    DESIRED_EYE_DISTANCE,
    LEFT_EYE_IDX,
    RIGHT_EYE_IDX,
    eye_y_ratio
)

print("Final canonical landmarks:")
print(canonical_rescaled)


######### align images #########

# make a list of files we need
coord_list = list_files_df(landmarks_dir, ".txt")
face_list = list_files_df(image_dir, ".jpg")

# loop
for i in range(nFaces):

    # input image
    input_image_path = os.path.join(image_dir, face_list.filename[i])

    # input image landmark coordinates
    f = coord_list.filename[i]
    f_path = os.path.join(landmarks_dir, f)
    input_landmarks = np.loadtxt(f_path, dtype=np.float32)
    
    # run alignment
    aligned_face = align_face_image(
        input_image_path,
        input_landmarks,
        canonical_rescaled,
        OUTPUT_SIZE,
        output_dir
    )

