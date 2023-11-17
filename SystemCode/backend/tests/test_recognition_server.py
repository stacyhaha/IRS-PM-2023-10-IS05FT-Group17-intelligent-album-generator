# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_recognition_server.py
   Author :        
   time：          
   last edit time: 
   Description :   测试图片识别模型
-------------------------------------------------
"""
import os
import json
import unittest
from album.recognition_server.recognition_server import RecognitionServer

class TestRecognitionServer(unittest.TestCase):
    def test_recognition_server(self):
        """
        测试方式：
        终端：
        python3.6 -m unittest tests/test_recognition_server.py
        """
        server = RecognitionServer(
            weights_path = r'/Users/stacy/iss/places365-master/resnet50_places365.pth.tar',
            categories_file = r'/Users/stacy/iss/places365-master/categories_places365.txt'
            )
        inputs = {
            "Input": "/Users/stacy/Downloads/IMG_6194.HEIC"
        }
        result = server.predict(**inputs)
        import pprint
        pprint.pprint(result)
        

