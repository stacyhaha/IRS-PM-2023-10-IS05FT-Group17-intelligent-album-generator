# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ratio_extractor.py
   Author :
   time：
   last edit time:
   Description :   图片比例识别模型
-------------------------------------------------
"""
import pyheif
from PIL import Image
from pathlib import Path

class RatioExtractor:
    def __init__(self):
        pass


    def predict(self, Input, **kwargs):
        """
        * input: 输入单张图片的路径
        * output: 输出图片长宽比

        example:
        * input: "images/image1.png"
        * output: 0.5
        """
        try:
            if Input.lower().endswith("heic"):
                image = self.transfer_heic_file(Input)
            else:
                image = Image.open(Input)
            width, height = image.size
            return width / height if height != 0 else 0  # avoid zero division error
        except Exception as e:
            print(f"Error reading photo info: {str(e)}")
            return None
        

    def transfer_heic_file(self, image_path):
        img_path = Path(image_path)
        img_binary = img_path.open("rb").read()
        heif_file = pyheif.read(img_binary)
        img = Image.frombytes(data=heif_file.data, mode=heif_file.mode, size=heif_file.size)
        return img

if __name__ == "__main__":
    image_path = r"/Users/stacy/Downloads/IMG_6194.HEIC"
    Ratio_extractor = RatioExtractor()
    photo_Ratio = Ratio_extractor.predict(image_path)

    if Ratio_extractor:
        print(f"Aspect Ratio: {photo_Ratio:.2f}")
    else:
        print("No Exif data found in the photo.")