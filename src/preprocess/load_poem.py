#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
#@Time    : 2019/7/12 12:54
# @Author  : MaCan (ma_cancan@163.com)
# @File    : load_poem.py
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import os
import json
import time
import re

from pyspark import SparkConf, Row
from pyspark.sql import SparkSession

from src.preprocess.io_utils import read_file


formats = {
    #'youmengying':['content'],
    #'ci':['paragraphs', 'rhythmic'],
    'json': ['paragraphs', 'title'],
    #'shijing': ['content', 'title', 'chapter', 'section'],
    #'wudai': ['paragraphs', 'title']
}

def _parser(datas, category='json'):
    """
    解析不同类型json数据
    幽梦影：content
    ci宋词:paragraphs， rhythmic
    wudai:paragraphs, title
    json宋：paragraphs, title
    诗经:content, title, chapter, section
    :param datas:
    :param filter_dict 只统计字典中的字
    :return:
    """
    docs = []
    for data in datas:
        if type(data) == str:
            print(datas)
            continue
        fm = formats.get(category, None)
        content = ''
        for f in fm:
            doc = data.get(f, '')
            if doc == '':
                continue
            content += ''.join(doc)
        docs.append(content)
    return docs


def load_poem(file_path):
    """
    读取古诗词
    :param file_path:
    :return:
    """
    if not os.path.isdir(file_path):
        raise FileNotFoundError
    for dir in os.listdir(file_path):
        curr_dir = os.path.join(file_path, dir)
        if not os.path.isdir(curr_dir) or dir not in formats.keys():
            continue

        print('now process dir: \'{}\''.format(dir))
        for file in os.listdir(curr_dir):
            curr_file = os.path.join(curr_dir, file)
            if not os.path.isfile(curr_file) or file[-4:] != 'json':
                continue
            print('\t file: {}'.format(curr_file))

            with open(curr_file, 'r', encoding='utf-8') as fd:
                data = json.load(fd)
                #print(data)
                # 解析当前文件的古诗词信息
                doc = _parser(data, dir)
                yield doc


def save_poem_content(docs, save_path):
    """
    将古诗词的文本形式存储到文件中，用于词的共现统计
    :param docs:
    :param save_path:
    :return:
    """
    with open(save_path, 'w', encoding='utf-8') as fd:
        for doc in docs:
            for line in doc:
                fd.write(line + '\n')


def combine_words(line, filter_dict=None):
    """
    将古诗词进行分字, 并进行共现组合
    :param line:
    :return:
    """
    line = re.sub('[。,，.?!！？￥%&\'\\"]', '', line.strip())
    if filter_dict is None:
        words = list(line)
    else:
        words = [x for x in list(line) if x in filter_dict]
    rst = []
    for i in range(len(words)):
        for j in range(i, len(words)):
            if words[i] == words[j]:
                continue
            # if words[i] < words[j]:
            #     rst.append(((words[i], words[j]), line))
            # else:
            #     rst.append(((words[j], words[i]), line))
            if words[i] < words[j]:
                rst.append((words[i], words[j]))
            else:
                rst.append((words[j], words[i]))
    return rst


def load_and_split(spark, filter_dict):
    """

    :param spark:
    :param filter_dict:
    :return:
    """
    data = spark.read.text('poem.txt').distinct()
    data.show()
    seg = data.rdd.flatMap(lambda x: combine_words(x[0], filter_dict))
    return seg


def word_count_and_sorted(spark, data):
    data = data\
        .map(lambda word: (word, 1))\
        .reduceByKey(lambda x, y: x + y)\
        .map(lambda x: (x[1], x[0]))\
        .sortByKey(False)\
        .map(lambda x: Row(word=x[1], count=x[0]))
    return spark.createDataFrame(data)


def load_local_name_record(path):
    """
    加载班级信息名录，只统计班级同学名称的字，减少计算量
    :param path:
    :return:
    """
    import xlrd
    book = xlrd.open_workbook(path)
    tabel = book.sheet_by_index(0)
    nrow = tabel.nrows
    contain_token_dict = set()
    for row in range(1, nrow):
        name = tabel.cell(row, 1).value[1:]
        contain_token_dict = contain_token_dict.union(set(list(name)))
    return contain_token_dict


if __name__ == '__main__':
    path = '/Users/macan/Desktop/chinese-poetry-master' # 古诗词路径
    class_name_tabel_path = '/Users/macan/Desktop/Vcamp/2019Vcamp 3班班级通讯录.xlsx' # 班级通讯录路劲
    # 加载班级通讯录，得到同学姓名信息
    filter_dict = load_local_name_record(class_name_tabel_path)

    # docs = load_poem(path)
    # save_poem_content(docs, 'poem.txt')

    conf = SparkConf()
    spark = SparkSession \
        .builder \
        .appName('co-word-count') \
        .master('local[*]') \
        .config(conf=conf) \
        .getOrCreate()

    seg = load_and_split(spark, filter_dict)
    counts = word_count_and_sorted(spark, seg)
    counts.show(200)
    spark.stop()


