# coding=utf-8

import json
from datetime import date, datetime
import xmlrpc.client
from decimal import Decimal
import os
import re

import dateutil.parser
import treelib

import datetime_utils


DATA_DIR = os.path.abspath(os.path.join(os.path.curdir, './data'))
PAGES_JSON_FILE_PATH = os.path.join(DATA_DIR, 'pages.json')

def format_dic(dic):
    """将 dic 格式化为 JSON，处理日期等特殊格式"""
    for key, value in dic.items():
        dic[key] = format_value(value)
    return dic


def format_value(value):
    if isinstance(value, dict):
        return format_dic(value)
    elif isinstance(value, list):
        return format_list(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, date):
        return value.isoformat()
    elif isinstance(value, xmlrpc.client.DateTime):
        dt = dateutil.parser.parse(value.value)
        return datetime_utils.naive2aware(dt).isoformat()
    elif isinstance(value, Decimal):
        return float(value)
    else:
        return value


def format_list(l):
    return [format_value(x) for x in l]


def sort_pages(pages):
    tree = treelib.Tree()
    root_page = pages[0]
    tree.create_node(root_page['title'], root_page['id'], data=root_page)
    for page in pages[1:]:
        tree.create_node(page['title'], page['id'], parent=root_page['id'], data=page)
    for page in pages[1:]:
        if page['parentId'] == '0':
            continue
        tree.move_node(page['id'], page['parentId'])
    pages_ordered = []
    for page_id in tree.expand_tree(mode=tree.WIDTH):
        pages_ordered.append(tree[page_id].data)
    return pages_ordered


def load_pages():
    with open(PAGES_JSON_FILE_PATH, 'r') as pages_file:
        return json.loads(pages_file.read())


def add_prefix_to_traceback(e):
    return re.sub('^', '! ', str(e))
