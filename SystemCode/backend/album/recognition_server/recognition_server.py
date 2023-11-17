# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     recognition_server.py
   Author :        
   time：          
   last edit time: 
   Description :   识别服务，内部调用多个模型
-------------------------------------------------
"""
import json
from .recognition_models.time_extractor import TimeExtractor
from .recognition_models.ratio_extractor import RatioExtractor
from .recognition_models.main_colors_extractor import MainColorsExtractor
from .recognition_models.background_extractor import BackgroundExtractor

class RecognitionServer:
    def __init__(self, weights_path, categories_file):
        self.time_extractor = TimeExtractor()
        self.ratio_extractor = RatioExtractor()
        self.main_colors_extractor = MainColorsExtractor()
        self.background_extractor = BackgroundExtractor(weights_path, categories_file)
        return
    
    def predict(self, Input, **kwargs):
        """
        * Input: 输入单张图片的路径
        * output: 输出图片的属性
        * description: 依次调用识别服务，内部调用多个模型

        example:
        * input: "images/image1.png"
        * output: {
            "time_extractor": "2023-08-04 22:23:53"
	}
        """
        user_config = kwargs.get("user_config", {})
        recognition_server_config = user_config.get("recognition_server", {})

        image_capture_time = self.time_extractor.predict(Input)
        image_ratio = self.ratio_extractor.predict(Input)
        image_main_colors = self.main_colors_extractor.predict(Input)
        if recognition_server_config.get("background_detection", "on") == "on":
            image_background = self.background_extractor.predict(Input)
            result = {
                "image": Input,
                "time_extractor": image_capture_time,
                "ratio_extractor": image_ratio,
                "main_colors_extractor": image_main_colors,
                "background_extractor": image_background
            }
        else:
            result = {
                "image": Input,
                "time_extractor": image_capture_time,
                "ratio_extractor": image_ratio,
                "main_colors_extractor": image_main_colors
            }
        
        return result
    

    