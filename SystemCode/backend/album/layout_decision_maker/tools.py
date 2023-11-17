# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：tools.py
   Author :  XIANGYI
   time：          
   last edit time: 
   Description :   
-------------------------------------------------
"""

import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from itertools import permutations

class Color:
    def __init__(self):
        self.color_map = [
            [253, 83, 8],
            [250, 153, 0],
            [250, 188, 0],
            [254, 254, 52],
            [208, 234, 44],
            [102, 176, 50],
            [3, 145, 206],
            [1, 71, 254],
            [60, 1, 164],
            [133, 0, 175],
            [167, 24, 76],
            [254, 38, 19]
            ]
        self.color_map_lab = np.array([self.rgb2lab(*i) for i in self.color_map])
    

    def find_closed_color(self, r, g, b):
        l, a, b = self.rgb2lab(r, g, b)
        lab = np.array([l, a, b])
        color_index = ((self.color_map_lab - lab) ** 2).sum(axis=1).argmax()
        return color_index
    
    def generate_color_distribution(self, main_colors):
        """
        the format of main_colors like:
        [[2,3,44,], 0.2], [2,99, 2], 0.9]]
        """
        df = pd.DataFrame(main_colors, columns=["rgb", "ratio"])
        df["ratio"] = df["ratio"]/df["ratio"].sum()
        df["closed_color_index"] = df["rgb"].apply(lambda x: self.find_closed_color(*x))
        
        color_distribution = np.zeros(len(self.color_map))
        for i in range(df.shape[0]):
            closed_color_index = df.iloc[i]["closed_color_index"]
            ratio = df.iloc[i]["ratio"]

            for move_step, weight in zip([0, 1, -1, 2, -2], [9/15, 2/15, 2/15, 1/15, 1/15]):
                try:
                    next_index = (closed_color_index + move_step) % len(self.color_map)
                    color_distribution[next_index] = max(
                        color_distribution[next_index], 
                         ratio * weight
                        )
                except:
                    import pdb;pdb.set_trace()
        return color_distribution

    def rgb2lab(self, r, g, b):
        rgb_color = np.array([r, g, b], dtype=np.uint8)
        lab_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2Lab)
        L, a, b = lab_color[0][0]
        return L, a, b
    
    def cal_color_diff(self, main_colors_in_one_page):
        """
        the format of main_colors_in_one_page like:
        [
            [[2,3,44,], 0.2], [2,99, 2], 0.9]],
            [[2,3,44,], 0.2], [2,99, 2], 0.9]]
        ]
        """
        color_distribution_in_one_page = []
        for i in main_colors_in_one_page:
            this_distribution = self.generate_color_distribution(i)
            color_distribution_in_one_page.append(this_distribution)
        diff = np.array(color_distribution_in_one_page).mean(axis=0).std()
        return diff

def cal_diff_in_time(x):
    """
    calculate the difference in time
    when calculating the standard deviation of a time, minutes are ignored.

    input:
    x: type: pd.dataframe
    """
    reserve_hour = x.time_extractor.apply(lambda i: datetime.strptime(i, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:00:00"))
    reserve_hour = reserve_hour.apply(lambda i: datetime.strptime(i, "%Y-%m-%d %H:%M:%S").timestamp() // 3600)
    if len(reserve_hour) == 1:
        return 0
    return reserve_hour.std()


def cal_diff_in_background(x):
    background_counter = x.background_extractor.value_counts().to_dict()
    count = x.background_extractor.count()
    gini = 1 - ((np.array(list(background_counter.values())) / count) ** 2).sum()
    return gini


def cal_diff_in_ratio(x, template_manager):
    """
    return the diff value and the best align
    example:
    output:
    {
        "value": 2.9,
        "align": [{"image": "xxx.png", "template_name": "A4_2_2", "index": 2}]
    }
    """
    image_num = len(x)

    permutation_index = [i for i in permutations(list(range(image_num)))]
    permutation_index_df = pd.DataFrame(np.array(permutation_index)).T
    image_ratio_df = permutation_index_df.replace(x.ratio_extractor.to_dict())

    template_list = [i["template_name"] for i in template_manager.template_json[image_num].values()]
    template_ratio_list = [template_manager.template_dict[t]["ratio"] for t in template_list ]
    template_ratio_array = np.array(template_ratio_list)[..., np.newaxis]
    template_tile = np.tile(template_ratio_array, (image_ratio_df.shape[1]))
    
    try:
        diff = abs(image_ratio_df.values - template_tile).mean(1)
    except:
        import pdb;pdb.set_trace()
    min_index = np.argmin(diff)
    value = np.min(diff)
    row, col = divmod(min_index, image_ratio_df.shape[1])
    
    best_template = template_list[row]
    best_permutation_index = permutation_index_df.iloc[:, col]
    align = pd.DataFrame({"image": x.image, "template": best_template, "index": best_permutation_index.values, "time": x.time_extractor}).to_dict("record")
    return {"value": value, "align": align}
