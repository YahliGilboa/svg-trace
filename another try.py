import os
import subprocess
import tempfile

import numpy
import numpy as np
import svgutils.transform as sg
from PIL import Image, ImageFile
from skimage.filters import median
from skimage.morphology import disk
from sklearn.cluster import KMeans
import svg_stack as ss

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

        # TODO: consider coloring the figures for bettesr 3d model creation in 3mf, so maybe create figs here already
        # https: // stackoverflow.com / questions / 3380726 / converting - an - rgb - color - tuple - to - a - hexidecimal - string
        file_paths = []
        for i in range(len(primary_color_palette)):
            # for i in range(1):
            mask = (min_diffs == i).astype(np.uint8) * 255
            mask = median(mask, disk(3))

            temp_folder_file_path = os.path.join(d, str(i))
            # print(temp_folder_file_path)
            Image.fromarray(mask).save(f"{temp_folder_file_path}.bmp")

            print(f"{temp_folder_file_path}.svg")
            subprocess.run(["potrace", f"{temp_folder_file_path}.bmp", "-s", "-o", f"{temp_folder_file_path}.svg"])
            subprocess.run(["potrace", f"{temp_folder_file_path}.bmp", "-s", "-o", f"bro{i}.svg"])

            file_paths.append(f"{temp_folder_file_path}.svg")

        # assuming 0 is the background- elaborate in next comment
        base_figure = sg.fromfile(os.path.join(d, '1.svg'))
        figs = [sg.fromfile(file_path) for file_path in file_paths]
        # the [2:] is an attempt to get rid of the trace of the background color; maybe there is a better way to do it
        # like letting the user select what it is, for now ill assume its the dominant color
        plots = [fig.getroot() for fig in figs[2:]]

        base_figure.append(plots)
        base_figure.save("readied_svg.svg")





def get_color_mask_from_img(img: list[numpy.ndarray], mask_color_lab: numpy.ndarray) -> list[numpy.ndarray]:
    '''this function takes in an image and the color pallete and returns all masks (images of colors) as a tuple'''

    pass


def calculate_main_image_colors(img_colors_rgb, colors_n=2):
    # model to cluster
    kmeans = KMeans(n_clusters=colors_n).fit(img_colors_rgb)

    # round results into int and return
    return np.round(kmeans.cluster_centers_).astype(int)


main()
