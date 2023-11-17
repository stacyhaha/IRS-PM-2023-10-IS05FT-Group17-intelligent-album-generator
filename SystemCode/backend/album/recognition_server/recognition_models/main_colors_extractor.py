# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     main_colors_extractor.py
   Author :
   time：
   last edit time:
   Description :   识别图片的主要颜色
-------------------------------------------------
"""
import pyheif
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
from pathlib import Path

class MainColorsExtractor:
    def __init__(self, n_colors=3):
        self.n_colors = n_colors

    def predict(self, Input, **kwargs):
        """
        * input: 输入单张图片的路径
        * output: 输出图片的主要颜色

        example:
        * input: "images/image1.png"
        * output: [
            [(233,3,4), 0.8],
            [(12, 45, 2), 0.1],
            [(87,22, 222), 0.1]
        ]  # list[0]指颜色，list[1]指颜色在图片中的比例
        """
        # Open the image
        if Input.lower().endswith("heic"):
            image = self.transfer_heic_file(Input)
        else:
            image = Image.open(Input)

        # Resize for speed
        image = image.resize((100, 100))

        # Convert image to RGB
        image = image.convert('RGB')

        # Convert image to numpy array and reshape
        pixels = np.array(image).reshape(-1, 3)

        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=self.n_colors).fit(pixels)

        # Count the labels (how many pixels of each color)
        unique, counts = np.unique(kmeans.labels_, return_counts=True)

        # Sort colors by dominance
        sorted_indices = np.argsort(counts)[::-1]

        result = []
        for index in sorted_indices:
            dominance = counts[index] / len(pixels)
            result.append([tuple(kmeans.cluster_centers_[index].astype(int).tolist()), dominance])

        return result
    

    def transfer_heic_file(self, image_path):
        img_path = Path(image_path)
        img_binary = img_path.open("rb").read()
        heif_file = pyheif.read(img_binary)
        img = Image.frombytes(data=heif_file.data, mode=heif_file.mode, size=heif_file.size)
        return img


if __name__ == "__main__":
    image_path = r"/Users/stacy/Downloads/IMG_6194.HEIC"
    extractor = MainColorsExtractor()
    dominant_colors = extractor.predict(image_path)
    for color_info in dominant_colors:
        print(f"Color: {color_info[0]}, Dominance: {color_info[1]:.2f}")
