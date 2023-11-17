# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_album_maker.py
   Author :        
   time：          
   last edit time: 
   Description :   测试pdf生成模块
-------------------------------------------------
"""
import os
import json
import unittest
from album.album_maker.album_maker import AlbumMaker

class TestAlbumMaker(unittest.TestCase):
    def test_album_maker(self):
        """
        测试方式：
        终端：
        python3.6 -m unittest tests/test_album_maker.py
        """
        server = AlbumMaker()
        inputs = {
            "Input": "layout_decision_maker_result.json"
        }
        result = server.predict(**inputs)
        import pprint
        pprint.pprint(result)
        