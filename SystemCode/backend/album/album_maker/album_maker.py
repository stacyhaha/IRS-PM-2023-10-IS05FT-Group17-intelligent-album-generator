# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     album_maker.py
   Author :        
   time：          
   last edit time: 
   Description :   根据遗传算法的结果生成最后的pdf文件
-------------------------------------------------
"""
import os
import pyheif
import logging
import pandas as pd
from PIL import Image
from pathlib import Path
from PyPDF2 import PdfMerger
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

class AlbumMaker:
    def __init__(self):
        return
    
    def predict(self, layout_res, pdf_path, **kwargs):
        """
        * Input: 图片排版信息，例如tests/layout_decision_maker_result.json
        * output: 输出排版好的pdf文件路径

        example:
        * input: "tests/layout_decision_maker_result.json"
        * output: "album.pdf"
        """
        user_config = kwargs.get("user_config", {})
        
        # read image info
        image_df = pd.read_json(layout_res)
        image_df = pd.concat([image_df.drop("template_info", axis=1), pd.DataFrame(image_df.template_info.values.tolist())], axis=1)
        page_num = image_df.page_idx.max()
        
        
        dir_path = os.path.dirname(os.path.abspath(pdf_path))
        temp_dir = os.path.join(dir_path, datetime.now().strftime("%Y.%m.%d_%H.%M.%S"))
        os.mkdir(temp_dir)
        
        page_list = []
        for page_idx in range(1, page_num+1):
            this_page_image_df = image_df.loc[image_df.page_idx == page_idx]
            page_img = self.generate_one_page(this_page_image_df, user_config)
            page_path = os.path.join(temp_dir, f"{page_idx}.pdf")
            page_img.save(page_path)
            page_list.append(page_path)
        
        # merge
        pdf_merge = PdfMerger()
        for this_page in page_list:
            pdf_merge.append(this_page)
        pdf_merge.write(pdf_path)
        pdf_merge.close()
        logger.info("generate album pdf successfully!")
        logger.info(f"album pdf path: {pdf_path}")
        return

        
    def generate_one_page(self, image_df, user_config):
        background_color = user_config.get("background_color", (255, 255, 255))
        size = image_df.template_size.iloc[0]
        page = Image.new(mode="RGB", size=size, color=tuple(background_color))

        for i in range(image_df.shape[0]):
            img = self.edit_image(image_df.iloc[i]["image"], image_df.iloc[i]["location"])
            page.paste(img, (int(image_df.iloc[i]["location"][0]), int(image_df.iloc[i]["location"][1])))
        return page
        


    def edit_image(self, image_path, template_loc):
        if image_path.lower().endswith("heic"):
            img = self.transfer_heic_file(image_path).convert("RGB")
        else:
            img = Image.open(image_path).convert("RGB")
            
        # resize
        img_ratio = img.size[0] * 1.0 / img.size[1]
        template_width = template_loc[2] - template_loc[0]
        template_height = template_loc[3] - template_loc[1]
        template_ratio = template_width / template_height
        
        if img_ratio / template_ratio <= 1:
            # extend width
            extend_width = template_width
            extend_height = extend_width * 1.0 / img.size[0] * img.size[1]
        else:
            # extend height
            extend_height = template_height
            extend_width = extend_height * 1.0 / img.size[1] * img.size[0]
        resized_img = img.resize((int(extend_width), int(extend_height)))

        # crop
        x1 = int((extend_width - template_width) / 2)
        x2 = min(x1 + int(template_width), resized_img.size[0])
        y1 = int((extend_height - template_height) / 2)
        y2 = min(y1 + int(template_height), resized_img.size[1])
        croped_img = resized_img.crop([x1, y1, x2, y2])

        return croped_img
    
    def transfer_heic_file(self, image_path):
        img_path = Path(image_path)
        img_binary = img_path.open("rb").read()
        heif_file = pyheif.read(img_binary)
        img = Image.frombytes(data=heif_file.data, mode=heif_file.mode, size=heif_file.size)
        return img


if __name__ == "__main__":
    album_maker = AlbumMaker()
    album_maker.predict(
        "/Users/stacy/iss/smart_album_generator/tests/layout_decision_maker_result.json",
        "album.pdf"
                       )