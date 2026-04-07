import os
import subprocess
import tempfile

import numpy
import numpy as np
import svgutils.transform as sg
from PIL import Image, ImageFile
from skimage.filters import median
from skimage.morphology import disk

# 2 approaches here-
# 1. use a color tolerance and select everything in that color tolerance and include it in mask
# 2. calculate what primary color each pixel is closest to, and color the pixel to be that primary color. create a mask from it
# method NO#1 is simpler, but if no color falls into this tolerance what will happen?
# therefore ill be using method NO 2
from src.calculate_dominant_colors import calculate_main_image_colors

ORIGINAL_COLOR_OF_SVG = "#000000"


def convert_img_to_svg(img_np_array: np.array, color_pallete: np.array,save_file_path:str):
    # here get additional colors from user and append them
    # additional_palette = np.empty(shape=(0, 3), dtype=int)
    # additional_palette = np.append(additional_palette, [[254, 216, 107], [122, 54, 15], [75, 22, 16]], axis=0)
    # primary_color_palette = np.append(default_palette, additional_palette, axis=0)
    print("Main colors (RGB):", color_pallete)

    image_coupled_with_primary_colors = img_np_array[:, :, np.newaxis, :] - color_pallete[np.newaxis,
                                                                               np.newaxis, :, :]
    diffs = np.sqrt(np.sum(np.square(image_coupled_with_primary_colors), axis=3))
    min_diffs = np.argmin(diffs, axis=2)

    with tempfile.TemporaryDirectory() as d:
        figs = []
        for i in range(len(color_pallete)):
            # for i in range(1):
            mask = (min_diffs == i).astype(np.uint8) * 255
            mask = median(mask, disk(3))

            temp_folder_file_path = os.path.join(d, str(i))
            Image.fromarray(mask).save(f"{temp_folder_file_path}.bmp")

            subprocess.run(
                ["potrace", f"{temp_folder_file_path}.bmp", "-s", "-i", "-o", f"{temp_folder_file_path}.svg"])
            # subprocess.run(["potrace", f"{temp_folder_file_path}.bmp", "-s", "-i", "-o", f"bro{i}.svg"])

            with open(f"{temp_folder_file_path}.svg", 'r') as f:
                content = f.read()

            content = content.replace(ORIGINAL_COLOR_OF_SVG, "#{:02x}{:02x}{:02x}".format(*color_pallete[i]))

            with open(f"{temp_folder_file_path}.svg", 'w') as f:
                f.write(content)

            fig = sg.fromfile(os.path.join(d, f"{temp_folder_file_path}.svg"))

            figs.append(fig)


        # assuming 0 is the background- elaborate in next comment
        base_figure = figs[0]
        # the [2:] is an attempt to get rid of the trace of the background color; maybe there is a better way to do it
        # like letting the user select what it is, for now ill assume its the dominant color
        plots = [fig.getroot() for fig in figs[1:]]

        base_figure.append(plots)
        base_figure.save(save_file_path)


def get_color_mask_from_img(img: list[numpy.ndarray], mask_color_lab: numpy.ndarray) -> list[numpy.ndarray]:
    '''this function takes in an image and the color pallete and returns all masks (images of colors) as a tuple'''

    pass
