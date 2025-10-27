import cv2
import numpy as np
import svgwrite
from sklearn.cluster import KMeans
from scipy.spatial import ConvexHull


def png_to_colored_svg(input_png_path, output_svg_path, n_colors=5):
    """
    Converts a PNG to a multi-color SVG using k-means clustering.

    Args:
        input_png_path (str): Path to input PNG
        output_svg_path (str): Path to save output SVG
        n_colors (int): Number of dominant colors to trace
    """
    # Load image
    img = cv2.imread(input_png_path, cv2.IMREAD_UNCHANGED)
    if img.shape[2] == 4:
        # Remove alpha channel for clustering
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, c = img.shape

    # Flatten pixels for k-means
    pixels = img.reshape(-1, 3)

    # Cluster colors
    kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(pixels)
    labels = kmeans.labels_
    colors = kmeans.cluster_centers_.astype(int)

    # Prepare SVG
    dwg = svgwrite.Drawing(output_svg_path, size=(w, h))

    for i, color in enumerate(colors):
        mask = labels.reshape(h, w) == i
        ys, xs = np.where(mask)
        points = list(zip(xs, ys))
        if len(points) < 3:
            continue

        # Convex hull to get polygon per color
        hull = ConvexHull(points)
        polygon = [(int(points[v][0]), int(points[v][1])) for v in hull.vertices]

        # Add polygon with proper RGB integers
        dwg.add(
            dwg.polygon(
                polygon,
                fill=svgwrite.rgb(int(color[0]), int(color[1]), int(color[2])),
                stroke='none'
            )
        )

    dwg.save()
    print(f"✅ Colored SVG saved: {output_svg_path}")


# Example usage
png_to_colored_svg("logo.png", "output.svg", n_colors=6)
