# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_dedup_server
   Author :        
   time：          
   last edit time: 
   Description :   测试去重服务
-------------------------------------------------
"""

import os
import json
import unittest
from album.dedup_server.dedup_server import DedupServer

class TestDedupServer(unittest.TestCase):
    def test_dedup_server(self):
        """
        测试方式：
        终端：
        python3.6 -m unittest tests/test_dedup_server.py
        """
        server = DedupServer()
        inputs = {
            "inputs": ["images/image1.png", "images/image2.png", "images/image3.png", "images/image4.png", "images/image5.png"]
        }
        result = server.predict(**inputs)
        import pprint
        pprint.pprint(result)