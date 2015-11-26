# coding=utf-8

import json
from datetime import date, datetime
import xmlrpc.client
from decimal import Decimal

import dateutil.parser

import datetime_utils

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

