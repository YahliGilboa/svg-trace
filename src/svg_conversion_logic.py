import os
import subprocess
import tempfile

import numpy
import numpy as np
import svgutils.transform as sg
from PIL import Image
from skimage.filters import median
from skimage.morphology import disk

# 2 approaches here-
# 1. use a color tolerance and select everything in that color tolerance and include it in mask
# 2. calculate what primary color each pixel is closest to, and color the pixel to be that primary color. create a mask from it
# method NO#1 is simpler, but if no color falls into this tolerance what will happen?
# therefore ill be using method NO 2

COLOR_OF_SVG_TRACE = "#000000"


def convert_img_to_svg(img_np_array: np.array, color_pallete: np.array, excluded_colors:np.array, save_file_path: str):
    # here get additional colors from user and append them
    # additional_palette = np.empty(shape=(0, 3), dtype=int)
    # additional_palette = np.append(additional_palette, [[254, 216, 107], [122, 54, 15], [75, 22, 16]], axis=0)
    # primary_color_palette = np.append(default_palette, additional_palette, axis=0)
    image_coupled_with_primary_colors = img_np_array[:, :, np.newaxis, :] - color_pallete[np.newaxis,
                                                                            np.newaxis, :, :]
    diffs = np.sqrt(np.sum(np.square(image_coupled_with_primary_colors), axis=3))
    min_diffs = np.argmin(diffs, axis=2)

    with tempfile.TemporaryDirectory() as d:
        figs = []
        for i,value in enumerate(color_pallete):
            print(np.all(value == excluded_colors, axis=1))
            if np.all(value == excluded_colors, axis=1):
                continue

            mask = (min_diffs == i).astype(np.uint8) * 255
            mask = median(mask, disk(3))

            temp_folder_file_path = os.path.join(d, str(i))
            Image.fromarray(mask).save(f"{temp_folder_file_path}.bmp")

            subprocess.run(
                ["potrace", f"{temp_folder_file_path}.bmp", "-s", "-i", "-o", f"{temp_folder_file_path}.svg"])
            subprocess.run(["potrace", f"{temp_folder_file_path}.bmp", "-s", "-i", "-o", f"bro{i}.svg"])

            with open(f"{temp_folder_file_path}.svg", 'r') as f:
                content = f.read()

            content = content.replace(COLOR_OF_SVG_TRACE, "#{:02x}{:02x}{:02x}".format(*color_pallete[i]))

            with open(f"{temp_folder_file_path}.svg", 'w') as f:
                f.write(content)

            fig = sg.fromfile(os.path.join(d, f"{temp_folder_file_path}.svg"))

            figs.append(fig)

        base_figure = figs[0]
        plots = [fig.getroot() for fig in figs[1:]]

        base_figure.append(plots)
        base_figure.save(save_file_path)
