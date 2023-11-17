# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_layout_decision_maker.py
   Author :        
   time：          
   last edit time: 
   Description :   测试排版模型
-------------------------------------------------
"""
import os
import json
import unittest
from album.layout_decision_maker.layout_decision_maker import LayoutDecisionMaker

class TestLayoutDecisionMaker(unittest.TestCase):
    def test_layout_decision_maker(self):
        """
        测试方式：
        终端：
        python3.6 -m unittest tests/test_layout_decision_maker.py
        """
        server = LayoutDecisionMaker()
        inputs = {
            "Input": "recognition_result.json"
        }
        result = server.predict(**inputs)
        import pprint
        pprint.pprint(result)
        