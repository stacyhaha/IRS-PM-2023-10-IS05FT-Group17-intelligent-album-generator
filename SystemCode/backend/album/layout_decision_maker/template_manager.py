# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name: template_manager.py
   Author :  XIANGYI
   time:           
   last edit time: 
   Description :   
-------------------------------------------------
"""
import warnings
warnings.filterwarnings("ignore")

import os
import json 
import logging 
import pandas as pd
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


class TemplateManager:
    def __init__(self, template_dir):
        self.template_json = defaultdict(dict)
        self.read_template_file(template_dir)
        self.get_template_dict()
        

    def read_template_file(self, template_dir):
        all_files = os.listdir(template_dir)
        template_files = list(filter(lambda x:x.endswith(".json"), all_files))
        for this_file in template_files:
            t_file = os.path.join(template_dir, this_file)
            with open(t_file, "r") as f:
                content = f.read()
                this_template_json = json.loads(content)
                pic_num = int(this_file.split("_")[1])
                self.template_json[pic_num][this_template_json["template_name"]] = this_template_json

    
        logger.info("load the template files successfully")
        logger.info(f"load {len(template_files)} files")

    
    def get_template_num(self, pic_num):
        template_info = self.template_json.get(pic_num, {})
        return len(template_info)
    
    def get_template_dict(self):
        """
        change the format of template to
        {"A3_1_1": {"images":[[0.2, 0.3, 0.4 0.9]], "template_size": [792, 3345], "ratio": [0.2]}}
        """
        self.template_dict = {}
        for key, value in self.template_json.items():
            for this_template in value.values():
                template_name = this_template["template_name"]
                image = this_template["image"]
                template_size = this_template["template_size"]
                ratio = [self.get_ratio(*i) for i in image]
                self.template_dict[template_name] = {"images": image, "template_size": template_size, "ratio": ratio}
    
    def get_ratio(self, x1, y1, x2, y2):
        width = x2-x1
        height = y2-y1 
        ratio = width*1.0/height
        return ratio

    



if __name__ == "__main__":
    template_dir = "/Users/stacy/iss/smart_album_generator/templates"
    template_manager = TemplateManager(template_dir)
    import pdb;pdb.set_trace()
    template_manager.get_template_num(1)

        