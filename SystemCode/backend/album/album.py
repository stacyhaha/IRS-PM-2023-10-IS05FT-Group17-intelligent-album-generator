# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     album.py
   Author :        
   time：          
   last edit time: 
   Description :   integrate all parts
-------------------------------------------------
"""
import os
import json
import logging
from datetime import datetime
from .dedup_server.dedup_server import DedupServer
from .recognition_server.recognition_server import RecognitionServer
from .layout_decision_maker.layout_decision_maker import LayoutDecisionMaker
from .album_maker.album_maker import AlbumMaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

class Album:
    def __init__(self, workspace, weights_path, categories_file, template_dir):
        self.workspace = workspace
        self.dedup_server = DedupServer()
        self.recognition_server = RecognitionServer(weights_path, categories_file)
        self.layout_decision_maker = LayoutDecisionMaker(template_dir)
        self.album_maker = AlbumMaker()
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        logger.info("initiate succeessfully")

    def predict(self, image_dir, user_config):
        images = os.listdir(image_dir)
        images = list(
            filter(lambda x:x.lower().endswith("jpg") or x.lower().endswith("jpeg") or x.lower().endswith("heic"),
            images))
        logger.info(f"original images num: {len(images)}")
        images = [os.path.join(image_dir, i) for i in images]
        
        combined_images, excluded_images = self.dedup_server.predict(images)
        logger.info(f"dedup server process successfully")
        logger.info(f"unique images num: {len(excluded_images)}")
        
        recog_res = []
        # todo: later use multi processing
        for this_image in excluded_images:
            this_recog_res = self.recognition_server.predict(this_image, user_config=user_config)
            recog_res.append(this_recog_res)
            logger.info(f"finish recog image: {this_image}")
        datetime_now = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        usr_dir = os.path.join(os.path.dirname(image_dir), datetime_now)
        os.mkdir(usr_dir)
        recog_res_path = os.path.join(usr_dir, "recog_res.json")
        with open(recog_res_path, "w") as f:
            f.write(json.dumps(recog_res, ensure_ascii=False, indent=2))
        logger.info("recognition process suceess")
        
        layout_res_path = os.path.join(usr_dir, "layout_res.json")
        self.layout_decision_maker.predict(recog_res_path, layout_res_path, user_config=user_config)
        logger.info("layout decision process success")

        pdf_path = os.path.join(usr_dir, "album.pdf")
        album_maker_user_config = user_config.get("album_maker", {})
        self.album_maker.predict(layout_res_path, pdf_path, user_config=album_maker_user_config)
        logger.info("album maker process successfully")
        logger.info(f"album path: {pdf_path}")
        return pdf_path
        

if __name__ == "__main__":
    album = Album(
        workspace = "/Users/stacy/iss/workspace",
        weights_path = r'/Users/stacy/iss/places365-master/resnet50_places365.pth.tar',
        categories_file = r'/Users/stacy/iss/places365-master/categories_places365.txt',
        template_dir= "/Users/stacy/iss/smart_album_generator/templates"
    )
    user_config = {
        "recognition_server":{
            "background_detection": "on"
        },
        "layout_decison_maker": {
            "max_num_pics_in_one_page": 4
        },
        "album_maker":{
            "background_color": (255, 255, 255)
        }
    }
    album_path = album.predict("/Users/stacy/iss/images", {})
