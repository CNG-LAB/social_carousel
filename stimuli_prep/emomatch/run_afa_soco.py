import alignfaces as afa

faces_path = "/Path/in"
pfx = ""     # relevant input files may start with a string
sfx = "JPG"  # input image format

# generate landmarks
afa.get_landmarks(
    faces_path,
    file_prefix=pfx,
    file_postfix=sfx,
    start_fresh=True
)

# check landmark placement
afa.plot_faces_with_landmarks_one_by_one(faces_path)

# run alignment
aligned_path = afa.align_procrustes(
    faces_path,
    file_prefix=pfx,
    file_postfix=sfx,
    adjust_size="set_image_height", size_value = 512,
    color_of_result="grayscale"
)

# Get aligned landmarks
afa.get_landmarks(
    aligned_path,
    file_prefix=pfx,
    file_postfix=sfx,
)

# Make aperture
the_aperture, aperture_path = afa.place_aperture(aligned_path, 
                                                file_prefix=pfx,
                                                file_postfix=sfx,
                                                aperture_type="MossEgg",
                                                contrast_norm="max",
                                                color_of_result="grayscale")



