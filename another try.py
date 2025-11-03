import subprocess
import tempfile
import time

import numpy
import numpy as np
from PIL import Image, ImageFile
from skimage import color
from skimage.filters import median
from skimage.morphology import disk
from sklearn.cluster import KMeans
import os

import svgutils.transform as sg


# 2 approaches here-
# 1. use a color tolerance and select everything in that color tolerance and include it in mask
# 2. calculate what primary color each pixel is closest to, and color the pixel to be that primary color. create a mask from it
# method NO#1 is simpler, but if no color falls into this tolerance what will happen?
# therefore ill be using method NO 2

# COLOR_TOLERANCE = 30

def main():
    img: ImageFile = Image.open("photos/logo.png").convert("RGB")  # Load image
    img_as_np_array = np.array(img)

    flattened_img = np.array(img_as_np_array).reshape(-1, 3)  # gets only LAB of image as flat array

    default_palette = calculate_main_image_colors(flattened_img, colors_n=2)

    # here get additional colors from user and append them
    additional_palette = np.empty(shape=(0, 3), dtype=int)
    additional_palette = np.append(additional_palette, [[254, 216, 107], [122, 54, 15], [75, 22, 16]], axis=0)
    primary_color_palette = np.append(default_palette, additional_palette, axis=0)
    print("Main colors (RGB):", primary_color_palette)

    image_coupled_with_primary_colors = img_as_np_array[:, :, np.newaxis, :] - primary_color_palette[np.newaxis,
                                                                               np.newaxis, :, :]
    diffs = np.sqrt(np.sum(np.square(image_coupled_with_primary_colors), axis=3))
    min_diffs = np.argmin(diffs, axis=2)

    with tempfile.TemporaryDirectory() as d:
        fig = sg.SVGFigure("100cm", "100cm")

        for i in range(len(primary_color_palette)):
            mask = (min_diffs == i).astype(np.uint8) * 255
            mask = median(mask, disk(3))

            temp_folder_file_no_extension = os.path.join(d,str(i))
            Image.fromarray(mask).save(f"{temp_folder_file_no_extension}.bmp")

            subprocess.run(["potrace", f"{temp_folder_file_no_extension}.bmp", "-s", "-o", f"{temp_folder_file_no_extension}.svg"])
            root = sg.fromfile(f"{temp_folder_file_no_extension}.svg").getroot()

            fig.append([root])

        fig.save('broski.svg')
        # background = sg.fromfile(os.path.join(d,f'{0}.svg'))
        #
        # for i in range(1, len(primary_color_palette)):

        #     background.append(svg)
        #
        # background.save('broski.svg')




def get_color_mask_from_img(img: list[numpy.ndarray], mask_color_lab: numpy.ndarray) -> list[numpy.ndarray]:
    '''this function takes in an image and the color pallete and returns all masks (images of colors) as a tuple'''

    pass


def calculate_main_image_colors(img_colors_rgb, colors_n=2):
    # model to cluster
    kmeans = KMeans(n_clusters=colors_n).fit(img_colors_rgb)

    # round results into int and return
    return np.round(kmeans.cluster_centers_).astype(int)


main()
