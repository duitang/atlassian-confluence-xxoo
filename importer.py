# coding=utf-8

import json
import time
import os
import logging

import dateutil.parser

from api import old_confluence_api, new_confluence_api
import utils


logger = logging.getLogger(__name__)


def batch_import(name, func, *args, **kwargs):
    pages = utils.load_pages()
    ordered_pages = utils.sort_pages(pages)
    success_count = 0
    fail_count = 0
    for page in ordered_pages:
        try:
            func(page['id'], *args, **kwargs)
        except Exception as e:
            logger.debug(e)
            fail_count += 1
            continue
        time.sleep(0.1)
        success_count += 1
        logger.info('import %s, page: %s, title: %s, s/f/t: %d/%d/%d' % (
            name, page['id'], page['title'], success_count, fail_count, success_count + fail_count))
    logger.info('import %s, s/f/t: %d/%d/%d' % (
        name, success_count, fail_count, success_count + fail_count))


def import_page(page_id, parent_id):
    json_file_path = os.path.join(utils.DATA_DIR, 'pages', page_id + '.json')
    if not os.path.isfile(json_file_path):
        logger.error('no file %s' % json_file_path)
        return

    with open(json_file_path, 'r') as page_file:
        page = json.loads(page_file.read())
        content = u"""{info}\n本文档从旧 Wiki 导入，原 URL：%s\n\n原创建人：%s %s\n\n原最后更新人：%s %s\n{info}\n\n""" % (
            page['url'],
            page['creator'],
            dateutil.parser.parse(page['created']).strftime('%Y-%m-%d %H:%M:%S'),
            page['modifier'],
            dateutil.parser.parse(page['modified']).strftime('%Y-%m-%d %H:%M:%S'),
        ) + page['content']
        new_store_format = new_confluence_api.convertWikiToStorageFormat(content)
        new_confluence_api.storePage({
            #'id': page['id'],
            'space': 'DT',
            'parentId': parent_id,
            'title': page['title'],
            'content': new_store_format,
            # 'creator': page['creator'],
            'modified': page['modified'],
        })

