# -*- coding: utf-8 -*-
"""
@author: kebo
@contact: itachi971009@gmail.com

@version: 1.0
@file: api.py
@time: 2019-07-24 15:29

这一行开始写关于本文件的说明与解释
"""
from create_name import api_make_name
from src import api_match_name
from generation import api_generate


def api_gen_photo(name2):
    photo_name = name2
    if photo_name=="杨紫":
        photo_name = "杨紫2"
    hidden = "style{;}"
    if name2 in ["程萌","胡歌","李鸿斌","胡妍","张立","唐梅芝"]:
        hidden = "hidden"
    return photo_name,hidden

if __name__ == '__main__':
    name = "李志帅"
    name2,score = api_match_name(name)
    # name_child = api_make_name(name,name2,is_girl=True)
    print(name2,score)
    # poem = api_generate(name,name2)
    # print(poem)
    # print(name_child)