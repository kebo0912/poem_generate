# -*- coding: utf-8 -*-
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file: api_match_name.py
@time: 2019-07-24 14:59

这一行开始写关于本文件的说明与解释
"""
import os
from project_config import PROJECT_ROOT_PATH
import random
from src.preprocess.poem_token_analysis import find_max_co_name_info, read_name_dict_data, load_helper_dict



def api_match_name(name):
    name_dict = {"张立":"胡妍","李鸿斌":"程萌","唐梅芝":"胡歌","张一山":"杨紫",
                 "胡妍":"张立","程萌":"李鸿斌","胡歌":"唐梅芝","杨紫":"张一山"}
    if name in name_dict:
        target_name = name_dict[name]
        score = 0.01*(random.randint(90,99)+random.randint(1,10)*0.1+random.randint(1,10)*0.01)
    else:
        path = os.path.join(PROJECT_ROOT_PATH,"dataset")
        co_cnt, name_pair_dict, name_dict, black_list = load_helper_dict(path)
        # 测试输入姓名，得到对应的”有缘人“
        target_name, score = find_max_co_name_info(name, name_pair_dict, co_cnt, name_dict, black_list)
    if target_name == None:
        target_name = "404"
    return target_name,score


if __name__ == '__main__':
    names = ['张立', '胡妍', '谢腾', '杨紫','高策',"李志帅","李鸿斌"]
    for name in names:
        target_name, score = api_match_name(name)
        print('{} and {} match score:{}'.format(name, target_name, score))
