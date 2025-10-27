import subprocess

import numpy as np
from PIL import Image, ImageOps
from scipy.ndimage import label
from svgpathtools import svg2paths

x = r"download.png"
y = r"output.svg"




def svg_to_extrude(svg_file, height=5):
    paths, _ = svg2paths(svg_file)
    polygons = []
    for path in paths:
        poly = [(seg.start.real, seg.start.imag) for seg in path]
        polygons.append(polygon(points=poly))  # OpenSCAD polygon
    shape = union()(*polygons)
    return linear_extrude(height)(shape)


# def convert_png_to_pbm(input_png_path, output_pbm_path):
#     """
#     Converts a PNG image to PBM format.
#
#     Args:
#         input_png_path (str): The path to the input PNG file.
#         output_pbm_path (str): The path to save the output PBM file.
#     """
#     try:
#         # Open the PNG image
#         img = Image.open(input_png_path)
#
#         # Convert to '1' mode (1-bit pixels, black and white) for PBM
#         # PBM format is inherently monochrome.
#         img = img.convert('1')
#
#         # Save as PBM
#         img.save(output_pbm_path)
#         print(f"Successfully converted '{input_png_path}' to '{output_pbm_path}'")
#     except FileNotFoundError:
#         print(f"Error: Input file '{input_png_path}' not found.")
#     except Exception as e:
#         print(f"An error occurred during conversion: {e}")


def convert_png_to_pbm(input_png_path, output_pbm_path, threshold, noise_area=20):
    def broski(p,t1=90,t2=40):
        if p > t1:
            t=255
        # if p<= t1 and p>t2:
        #     t = (t1+t2)/2
        # if p<=t2:
        #     t=0
        return t
    """
    Converts a PNG image to a cleaned PBM (1-bit) for Potrace tracing.

    Args:
        input_png_path (str): Input PNG file path.
        output_pbm_path (str): Output PBM file path.
        threshold (int): 0-255 threshold for black/white separation.
        noise_area (int): Remove black blobs smaller than this area (pixels).
    """
    try:
        img = Image.open(input_png_path).convert("RGBA")
        alpha = img.split()[-1]  # handle transparency
        img = ImageOps.grayscale(img)

        # Binarize image
        img = img.point(lambda p: 255 if p >= threshold else 0)
        img = img.convert('1')

        # # Denoise tiny black blobs
        # arr = np.array(img)
        # structure = np.ones((3, 3), dtype=int)
        # labeled, num_features = label(arr == 0, structure)
        # for feature in range(1, num_features + 1):
        #     mask = labeled == feature
        #     if mask.sum() < noise_area:
        #         arr[mask] = 255
        #
        # img = Image.fromarray(arr)
        img.save(output_pbm_path)
        print(f"✅ Clean PBM saved: {output_pbm_path}")

    except FileNotFoundError:
        print(f"File not found: {input_png_path}")
    except Exception as e:
        print("Error:", e)

    # Example usage:
# input_file = "download.png"  # Replace with your PNG file name
input_file = "logo.png"  # Replace with your PNG file name
output_file = "output.pbm"  # Desired output PBM file name
convert_png_to_pbm(input_file, output_file, threshold=40)

subprocess.run(["potrace", output_file, "-s", "-o", "detingdere.svg"])

# png_to_svg(x, y)
