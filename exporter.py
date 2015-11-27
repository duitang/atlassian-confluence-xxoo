# coding=utf-8

import json
import time
import os
import logging

import treelib

from api import confluence_api
import utils


logger = logging.getLogger(__name__)


DATA_DIR = os.path.abspath(os.path.join(os.path.curdir, './data'))
PAGES_JSON_FILE_PATH = os.path.join(DATA_DIR, 'pages.json')


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


def dump_page_list():
    pages = confluence_api.getPages('duitang')  # very long time
    with open(PAGES_JSON_FILE_PATH, 'w') as pages_file:
        pages_file.write(json.dumps(utils.format_value(pages)))


def load_pages():
    with open(PAGES_JSON_FILE_PATH, 'r') as pages_file:
        return json.loads(pages_file.read())


def dump_page(page_id):
    page_id = page_id
    page = confluence_api.getPage(page_id)
    with open(os.path.join(DATA_DIR, 'pages', page_id + '.json'), 'w') as page_file:
        page_file.write(json.dumps(utils.format_value(page)))


def dump_pages():
    pages = load_pages()
    ordered_pages = sort_pages(pages)
    success_count = 0
    fail_count = 0
    for page in ordered_pages:
        try:
            dump_page(page['id'])
        except Exception as e:
            logger.debug(e)
            fail_count += 1
            continue
        time.sleep(0.1)
        success_count += 1
        logger.info('dump pages, s/f/t: %d/%d/%d' % (
            success_count, fail_count, success_count + fail_count))
    logger.info('dump pages, s/f/t: %d/%d/%d' % (
        success_count, fail_count, success_count + fail_count))


def dump_comments_for_page(page_id):
    comments = confluence_api.getComments(page_id)
    with open(os.path.join(DATA_DIR, 'comments', page_id + '.json'), 'w') as comments_file:
        comments_file.write(json.dumps(utils.format_value(comments)))


def dump_comments():
    pages = load_pages()
    ordered_pages = sort_pages(pages)
    success_count = 0
    fail_count = 0
    for page in ordered_pages:
        try:
            dump_comments_for_page(page['id'])
        except Exception as e:
            logger.debug(e)
            fail_count += 1
            continue
        time.sleep(0.01)
        success_count += 1
        logger.info('dump comments, page: %s, s/f/t: %d/%d/%d' % (
            page['id'], success_count, fail_count, success_count + fail_count))
    logger.info('dump comments, s/f/t: %d/%d/%d' % (
        success_count, fail_count, success_count + fail_count))

