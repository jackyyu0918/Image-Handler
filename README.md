# Similiar-Image-Finder

Similiar-Image-Finder is a program to extract similiar image in source folder.

ImageHash is used for calculating the hash value of images for comparision. (https://pypi.org/project/ImageHash/)
# How to use

Modify the root_dir to your source folder with images, and change worker_number variable (number of processes).

Modify the hash_diff_threshold variable to control the threshold of similarity determination.


# Pre-requirement
pip install Pillow

pip install imagehash
