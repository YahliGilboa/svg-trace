import numpy as np
from sklearn.cluster import KMeans


def calculate_main_image_colors(img: np.array, colors_n=2):
    # to get a list of pixels (list of RGBS) to run algorithem on.
    flattened_img = img.reshape(-1, 3)
    # model to cluster
    kmeans = KMeans(n_clusters=colors_n).fit(flattened_img)

    # round results into int and return
    return np.round(kmeans.cluster_centers_).astype(int)
