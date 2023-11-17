# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     GA.py
   Author :  XIANGYI
   time：          
   last edit time: 
   Description :   
-------------------------------------------------
"""

import json 
import logging 
import numpy as np
import pandas as pd
from album.layout_decision_maker.template_manager import TemplateManager
from album.layout_decision_maker.tools import cal_diff_in_time, cal_diff_in_background, Color, cal_diff_in_ratio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


class GA:
    def __init__(self, template_dir, recognition_result, user_config={}, n_generation=100, pop_size=50, cross_rate=0.3, mutation_rate=0.02):
        self.color = Color()
        
        self.template_manager = TemplateManager(template_dir)
        self.recognition_result = self.read_json_file(recognition_result)
        self.image_info_df = pd.read_json(recognition_result)
        self.DNA_size = len(self.recognition_result)
        print("self.DNA_SIZE", self.DNA_size)
        self.n_generation = n_generation
        self.pop_size = pop_size
        self.cross_rate = cross_rate
        self.mutation_rate = mutation_rate

        
        self.user_config = user_config
        if "max_num_pics_in_one_page" not in self.user_config:
            self.user_config["max_num_pics_in_one_page"] = 4


        self.pop = self.init_population()

    def read_json_file(self, file_name):
        with open(file_name, "r") as f:
            content = f.read()
            json_content = json.loads(content)
            logger.info(f"load json file {file_name} successfully")
        return json_content

        

    def init_population(self):
        """
        generate the first population
        """
        pop = []

        for i in range(self.pop_size):
            this_chrome = self.init_chrome()
            pop.append(this_chrome)
        return pop


    def init_chrome(self):
        chrome = []
        for i in range(self.DNA_size):
            page = np.random.randint(0, self.DNA_size)
            while not self.template_manager.get_template_num(chrome.count(page)+1):
                page = np.random.randint(0, self.DNA_size)
            chrome.append(page)
        return chrome
    
    
    def evolve(self, fitness):
        # evolve algorithm
        pop = self.select(fitness)
        pop_copy = pop.copy()
        for parent in pop:
            child = self.crossover(parent, pop_copy)
            child = self.mutate(child)
            parent[:] = child 
        self.pop = pop

    
    def get_fitness_based_on_chrome(self, chrome):
        """
        calculate the fitness
        
        factors to consider:
        difference of picture taking time
        difference of colors in one page
        dismatch of ratio in template
        num of picture in one page
        difference of picture background (if available)
        
        objective function:


        """
        self.image_info_df["page_idx"] = chrome
        grouped_page = self.image_info_df.groupby("page_idx", group_keys=True)
        diff_in_time = grouped_page.apply(lambda x: cal_diff_in_time(x)).mean()
        if "background_extractor" in self.image_info_df:
            diff_in_background = grouped_page.apply(lambda x: cal_diff_in_background(x)).mean()
        diff_in_color = grouped_page.apply(lambda x: self.color.cal_color_diff(x["main_colors_extractor"].values)).mean()
        
        dismatch_in_ratio_df = grouped_page.apply(lambda x: cal_diff_in_ratio(x, self.template_manager))
        dismatch_value = dismatch_in_ratio_df.apply(lambda x: x["value"]).mean()
        align = dismatch_in_ratio_df.apply(lambda x: x["align"]).to_list()

        num_in_page = grouped_page.apply(lambda x: len(x)).mean()
        
        # print("diff_in_time",s diff_in_time)
        # print("diff_in_color", diff_in_color)
        # print("dismatch_value", dismatch_value)
        # print("num_in_page", num_in_page)

        fitness_value = 5.0*diff_in_time + diff_in_color + dismatch_value - 4 * num_in_page
        if "background_extractor" in self.image_info_df:
            fitness_value += diff_in_background
            # print("diff in background", diff_in_background)
        # print("fitness_value", fitness_value)
        self.image_info_df = self.image_info_df.drop(["page_idx"], axis=1)

        return {"fitness_value": fitness_value, "align": align}
    
    def get_fitness(self, chromes):
        fitness_value = []
        align_list = []
        for this_chrome in chromes:
            v = self.get_fitness_based_on_chrome(this_chrome)
            fitness_value.append(v["fitness_value"])
            align_list.append(v["align"])
        return fitness_value, align_list

    def select(self, fitness):
        """
        the less fitness, the more probability
        """
        fit = np.array(fitness)
        probability = np.exp(-fit)/np.exp(-fit).sum()
        idx = np.random.choice(np.arange(self.pop_size), size=self.pop_size, replace=True, p=probability)
        return np.array(self.pop)[idx].tolist()

    def crossover(self, parent1, pop):
        """
        cross over
        """
        if np.random.rand() > self.cross_rate:
            return parent1 
        i_ = np.random.randint(0, self.pop_size, size=1).tolist()[0]
        parent2 = pop[i_]

        parent1 = np.array(parent1)
        parent2 = np.array(parent2)

        # get preserved DNA from parent1
        page_index_in_parent1 = list(set(parent1))
        cross_points = np.random.randint(0, 2, len(page_index_in_parent1)).astype(np.bool_) 
        select_pages_in_parent1 = np.array(page_index_in_parent1)[cross_points]
        keep_in_parent1 = np.where(np.isin(parent1, select_pages_in_parent1), parent1, np.zeros_like(parent1)-1)


        keep_in_parent2 = np.where(keep_in_parent1==-1, parent2, np.zeros_like(parent2)-1)
        empty_page_num = list(set(range(self.DNA_size))-set(keep_in_parent1))
        empty_page_idx = 0
        pending2check_page = np.unique(keep_in_parent2)
        
        # transfer page to never used
        new_keep_in_parent2 = keep_in_parent2.copy()
        for page in pending2check_page:
            if page == -1:
                continue
            if page in set(keep_in_parent1):
                new_keep_in_parent2[keep_in_parent2 == page] = empty_page_num[empty_page_idx]
                empty_page_idx += 1
        keep_in_parent2 = new_keep_in_parent2

        empty_page_num = list(set(range(self.DNA_size))-set(keep_in_parent1) - set(keep_in_parent2))
        empty_page_idx = 0
        pending2check_page = np.unique(keep_in_parent2)
        for page in pending2check_page:
            if page == -1:
                continue
            while not self.template_manager.get_template_num(np.count_nonzero(keep_in_parent2==page)):
                arg = np.argwhere(keep_in_parent2==page)[0]
                keep_in_parent2[arg] = empty_page_num[empty_page_idx]
                empty_page_idx += 1
        res = np.vstack([keep_in_parent1, keep_in_parent2]).max(axis=0).tolist()
        from collections import Counter
        if 5 in list(Counter(res).values()):
            import pdb;pdb.set_trace()
        return res


    def mutate(self, child):
        for point in range(self.DNA_size):
            if np.random.rand() < self.mutation_rate:
                swap_point = np.random.randint(0, self.DNA_size)
                swapA, swapB = child[point], child[swap_point]
                child[point], child[swap_point] = swapB, swapA
        return child
    

    def generate(self):
        for generation in range(self.n_generation):
            fitness_list, align_list = self.get_fitness(self.pop)
            self.evolve(fitness_list)
            best_idx = np.argmin(fitness_list)
            best_align = align_list[best_idx]
            print("generation idx:", generation, "best_fitness", np.array(fitness_list).min())
        res = self.postprocess(best_align)
        return res
    
    
    def postprocess(self, align):
        self.image_info_df["page"] = -1
        self.image_info_df["template"] = ""
        self.image_info_df["index"] = -1
        for page_idx in range(len(align)):
            for i in range(len(align[page_idx])):
                image_name = align[page_idx][i]["image"]
                idx = self.image_info_df.image==image_name
                self.image_info_df.loc[idx, "page"] = page_idx
                self.image_info_df.loc[idx, "template"] = align[page_idx][i]["template"]
                self.image_info_df.loc[idx, "index"] = align[page_idx][i]["index"]
        rank_info = self.image_info_df.groupby("page").apply(lambda x:x.time_extractor.min()).rank(ascending=True, method="first").to_dict()  # rank according to time
        self.image_info_df["page_idx"] = self.image_info_df["page"].map(rank_info)
        
        res = []
        for i in range(self.image_info_df.shape[0]):
            template_info = {}
            template_name = self.image_info_df.iloc[i]["template"]
            img_idx = int(self.image_info_df.iloc[i]["index"])
            template_info["template_idx"] = template_name
            template_info["img_idx"] = img_idx
            template_info["page_idx"] = int(self.image_info_df.iloc[i]["page_idx"])
            template_info["location"] = self.template_manager.template_dict[template_name]["images"][img_idx]
            template_info["template_size"] = self.template_manager.template_dict[template_name]["template_size"]

            res.append(
                {
                    "image": self.image_info_df.iloc[i]["image"],
                    "template_info": template_info
                 }
                       )
        return res

if __name__ == "__main__":
    ga = GA(
        template_dir= "/Users/stacy/iss/smart_album_generator/templates",
        recognition_result="/Users/stacy/iss/smart_album_generator/tests/recognition_result.json",
        )
    pop = ga.init_population()
    print(pop)

            


