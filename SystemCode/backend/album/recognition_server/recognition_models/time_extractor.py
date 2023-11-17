# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     time_extractor.py
   Author :        Ren Jianan
   time：
   last edit time:   2023/10/07
   Description :   时间识别模型，识别图片的拍摄时间
-------------------------------------------------
"""
import exifread
import datetime
import pyheif
from datetime import datetime
import re


class TimeExtractor:
    def __init__(self):
        pass

    def predict(self, Input, **kwargs):
        """
        * input: 输入单张图片的路径
        * output: 输出图片的拍摄时间

        example:
        * input: "images/image1.png"
        * output: "2023-09-07 00:23:00"
        """
        try:
            if Input.lower().endswith("heic"):
                return self.get_heic_datetime(Input)

            with open(Input, 'rb') as image_file:
                tags = exifread.process_file(image_file)
                for tag, value in tags.items():
                    if 'DateTime' in tag:
                        if 'DateTime' in tag:
                            date_str, time_str = str(value).split(" ")
                            formatted_date = date_str.replace(":", "-",2)
                            return f"{formatted_date} {time_str}"
                else:
                    return "2000-01-01 00:00:00"
        except Exception as e:
            print(f"Error reading photo info: {str(e)}")
            return "2000-01-01 00:00:00"

    def get_heic_datetime(self, heic_path):
        heif_file = pyheif.read(heic_path)
        res = re.search("\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}",str(heif_file.metadata)).group()
        res = datetime.strptime(res, "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        return res

if __name__ == "__main__":
    image_path = r"/Users/stacy/Downloads/IMG_6194.HEIC"
    time_extractor = TimeExtractor()
    photo_datetime = time_extractor.predict(image_path)

    if photo_datetime:
        print(f"Date and Time: {photo_datetime}")
    else:
        print("No Exif data found in the photo.")