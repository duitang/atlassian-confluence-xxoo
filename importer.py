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

NEW_SPACE_KEY = 'DT'


def find_page_title_to_page_id(pages, page_id):
    old_parent_id_title = dict([(x['id'], x['title']) for x in pages])
    if page_id not in old_parent_id_title:
        raise ValueError('cannot locate %s' % (page_id))
    try:
        new_parent_id = new_confluence_api.getPage(NEW_SPACE_KEY, old_parent_id_title[
            page_id])['id']
    except Exception as e:
        raise ValueError('cannot locate %s, e: %s' % (
            old_parent_id_title[page_id], e))
    return new_parent_id


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


def fetch_convert_content(prefix, content):
    content = prefix + content
    try:
        new_store_format = new_confluence_api.convertWikiToStorageFormat(content)
    except xmlrpc.client.Fault as e:
        if ('com.atlassian.confluence.content.render.xhtml.migration.exceptions.UnknownMacroMigrationException:'
            in e.faultString):
            new_store_format = new_confluence_api.convertWikiToStorageFormat(
                prefix + '{code}\n' + content.replace('{code}', r'\{code\}') +
                '\n{code}')
        else:
            raise e
    return new_store_format


def import_page(page_id, parent_id):
    json_file_path = os.path.join(utils.DATA_DIR, 'pages', page_id + '.json')
    if not os.path.isfile(json_file_path):
        logger.error('no file %s' % json_file_path)
        return

    with open(json_file_path, 'r') as page_file:
        page = json.loads(page_file.read())
        prefix = u"""{info}\n本文档从旧 Wiki 导入，原 URL：%s\n\n原创建人：%s %s\n\n原最后更新人：%s %s\n{info}\n\n""" % (
            page['url'],
            page['creator'],
            dateutil.parser.parse(page['created']).strftime('%Y-%m-%d %H:%M:%S'),
            page['modifier'],
            dateutil.parser.parse(page['modified']).strftime('%Y-%m-%d %H:%M:%S'),
        )
        new_store_format = fetch_convert_content(prefix, page['content'])
        logger.debug('convert page: %s, size: %d' % (page_id, len(page['content'])))
        try:
            new_confluence_api.storePage({
                'space': NEW_SPACE_KEY,
                'parentId': parent_id,
                'title': page['title'],
                'content': new_store_format,
                'modified': page['modified'],
            })
        except xmlrpc.client.Fault as e:
            if ('com.ctc.wstx.exc.WstxParsingException' in e.faultString):
                new_store_format = new_confluence_api.convertWikiToStorageFormat(
                    prefix + '{code}\n' + page['content'].replace('{code}', r'\{code\}') +
                    '\n{code}')
                logger.error('cannot insert convert, ignore, page id: %s, page title: %s' % (
                    page['id'], page['title']))
                new_confluence_api.storePage({
                    'space': NEW_SPACE_KEY,
                    'parentId': parent_id,
                    'title': page['title'],
                    'content': new_store_format,
                    'modified': page['modified'],
                })
            else:
                raise e


def import_pages():
    pages = utils.load_pages()
    ordered_pages = utils.sort_pages(pages)
    success_count = 0
    fail_count = 0
    SKIP_TO_ID = None
    for page in ordered_pages:
        if SKIP_TO_ID is not None:
            if page['id'] == SKIP_TO_ID:
                SKIP_TO_ID = None
            else:
                continue
        try:
            old_parent_id_title = dict([(x['id'], x['title']) for x in pages])
            if not page['parentId'] in old_parent_id_title and not page['parentId'] == '0':
                logger.error('No old parent, title: %s, old page id: %s' % (
                    page['title'], page['parentId']))
                return
            if page['parentId'] == '0':
                new_parent_id = '0'
            else:
                try:
                    new_parent_id = find_page_title_to_page_id(pages, page['parentId'])
                    # new_parent_id = new_confluence_api.getPage(NEW_SPACE_KEY, old_parent_id_title[
                    #     page['parentId']])['id']
                except Exception as e:
                    raise ValueError('cannot locate %s, e: %s' % (page['id'], e))
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


def import_attachments_for_page(page_id):
    json_file_path = os.path.join(utils.DATA_DIR, 'attachments', page_id + '.json')
    pages = utils.load_pages()
    if not os.path.isfile(json_file_path):
        logger.debug('no file %s' % json_file_path)
        return
    with open(json_file_path, 'r') as attachment_file:
        attachments = json.loads(attachment_file.read())

    for attachment in attachments:
        with open(os.path.join(utils.DATA_DIR, 'attachments', page_id + '_contents', attachment['id']),
                  'rb') as content_file:
            attachment_bin = content_file.read()
            new_confluence_api.addAttachment(find_page_title_to_page_id(
                pages, attachment['pageId']), {
                'fileName': attachment['fileName'],
                'contentType': attachment['contentType'],
                'comment': attachment['comment'] + ' | 导入日：%s，原作者： %s' % (
                    dateutil.parser.parse(attachment['created']).strftime('%Y-%m-%d %H:%M:%S'),
                    attachment['creator'],
                ),
            }, attachment_bin)


def import_comments_for_page(page_id):
    json_file_path = os.path.join(utils.DATA_DIR, 'comments', page_id + '.json')
    if not os.path.isfile(json_file_path):
        logger.debug('no file %s' % json_file_path)
        return
    with open(os.path.join(utils.DATA_DIR, 'comments', page_id + '.json'), 'r') as comments_file:
        comments = json.loads(comments_file.read())

    pages = utils.load_pages()
    for comment in comments:
        prefix = u"""{info}\n本文档从旧 Wiki 导入，原 URL：%s\n\n原创建人：%s %s\n\n原最后更新人：%s %s\n{info}\n\n""" % (
            comment['url'],
            comment['creator'],
            dateutil.parser.parse(comment['created']).strftime('%Y-%m-%d %H:%M:%S'),
            comment['modifier'],
            dateutil.parser.parse(comment['modified']).strftime('%Y-%m-%d %H:%M:%S'),
        )
        comment['modified'] = dateutil.parser.parse(comment['modified'])
        new_confluence_api.addComment({
            'pageId': find_page_title_to_page_id(pages, comment['pageId']),
            'title': comment['title'],
            'content': fetch_convert_content(prefix, comment['content']),
            'created': dateutil.parser.parse(comment['created']),
            'creator': comment['creator'],
        })


def import_attachments():
    batch_import('attachments', import_attachments_for_page)


def import_comments():
    batch_import('comments', import_comments_for_page)
