# coding=utf-8

import json
import time
import os
import logging
import xmlrpc.client

import dateutil.parser

from api import old_confluence_api, new_confluence_api
import utils


logger = logging.getLogger(__name__)

NEW_SPACE_KEY = 'T2'


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
        logger.debug('convert page: %s, size: %d' % (page_id, len(content)))
        try:
            new_store_format = new_confluence_api.convertWikiToStorageFormat(content)
        except xmlrpc.client.Fault as e:
            if ('com.atlassian.confluence.content.render.xhtml.migration.exceptions'
               '.UnknownMacroMigrationException:' in e.faultString):
                new_store_format = content
                logger.error('cannot format convert, ignore, page id: %s, page title: %s' % (
                    page['id'], page['title']))
            else:
                raise e
        new_confluence_api.storePage({
            #'id': page['id'],
            'space': NEW_SPACE_KEY,
            'parentId': parent_id,
            'title': page['title'],
            'content': new_store_format,
            # 'creator': page['creator'],
            'modified': page['modified'],
        })


def import_pages():
    pages = utils.load_pages()
    ordered_pages = utils.sort_pages(pages)
    success_count = 0
    fail_count = 0
    for page in ordered_pages:
        try:
            old_parent_id_title = dict([(x['id'], x['title']) for x in pages])
            if not page['parentId'] in old_parent_id_title and not page['parentId'] == '0':
                logger.error('No old parent, title: %s, old page id: %s' % (page['title'],
                                                                            page['parentId']))
                return
            if page['parentId'] == '0':
                new_parent_id = '0'
            else:
                try:
                    new_parent_id = new_confluence_api.getPage(NEW_SPACE_KEY, old_parent_id_title[
                        page['parentId']])['id']
                except Exception as e:
                    raise ValueError('cannot locate %s, e: %s' % (
                        old_parent_id_title[page['parentId']], e))
            import_page(page['id'], new_parent_id)
        except xmlrpc.client.Fault as e:
            if ('Transaction rolled back because it has been marked as rollback-only' in
                    e.faultString):
                logger.info('duplicate, page id: %s, title: %s' % (page['id'], page['title']))
            else:
                fail_count += 1
                logger.error('import error, page_id: %s, title: %s, e: %s' % (
                    page['id'], page['title'], e))
                raise e
        # time.sleep(0.01)
        success_count += 1
        logger.info('import %s, page: %s, title: %s, s/f/t: %d/%d/%d' % (
            'page', page['id'], page['title'], success_count, fail_count,
            success_count + fail_count))
    logger.info('import %s, s/f/t: %d/%d/%d' % (
        'page', success_count, fail_count, success_count + fail_count))
