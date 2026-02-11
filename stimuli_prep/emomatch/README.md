# Dependencies

Alignment of face images relies on the wonderful auto-face-align tool: https://github.com/SourCherries/auto-face-align 

# How to run the alignment

Update the paths and extensions as needed in run_afa_soco.py
Next, use afa_output_reshape.py (also update the paths) to place the image on a square, gray background. 

# What is SHINE? 

The SHINE (spectrum, histogram, and intensity normalization and equalization) toolbox enables control for a number of low-level image properties. Here, we use it to equate (as much as possible) image intensity histogram and spatial frequency content to minimize low-level feature confounds. 
Details here: https://link.springer.com/article/10.3758/BRM.42.3.671
