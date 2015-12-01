# coding=utf-8

import json
import time
import os
import logging

import treelib

from api import old_confluence_api
import utils


logger = logging.getLogger(__name__)


def dump_page_list():
    pages = old_confluence_api.getPages('duitang')  # very long time
    with open(utils.PAGES_JSON_FILE_PATH, 'w') as pages_file:
        pages_file.write(json.dumps(utils.format_value(pages)))


def dump_page(page_id):
    page = old_confluence_api.getPage(page_id)
    with open(os.path.join(utils.DATA_DIR, 'pages', page_id + '.json'), 'w') as page_file:
        page_file.write(json.dumps(utils.format_value(page)))


def batch_dump(name, func):
    pages = utils.load_pages()
    ordered_pages = utils.sort_pages(pages)
    success_count = 0
    fail_count = 0
    for page in ordered_pages:
        try:
            func(page['id'])
        except Exception as e:
            logger.debug(e)
            fail_count += 1
            continue
        time.sleep(0.1)
        success_count += 1
        logger.info('dump %s, page: %s, title: %s, s/f/t: %d/%d/%d' % (
            name, page['id'], page['title'], success_count, fail_count, success_count + fail_count))
    logger.info('dump %s, s/f/t: %d/%d/%d' % (
        name, success_count, fail_count, success_count + fail_count))


def dump_pages():
    batch_dump('page', dump_page)


def dump_comments_for_page(page_id):
    comments = old_confluence_api.getComments(page_id)
    if len(comments) == 0:
        return
    with open(os.path.join(utils.DATA_DIR, 'comments', page_id + '.json'), 'w') as comments_file:
        comments_file.write(json.dumps(utils.format_value(comments)))


def dump_comments():
    batch_dump('comment', dump_comments_for_page)


def dump_attachments_for_page(page_id):
    attachments = old_confluence_api.getAttachments(page_id)
    if len(attachments) == 0:
        return
    with open(os.path.join(utils.DATA_DIR, 'attachments', page_id + '.json'), 'w') as attachment_file:
        attachment_file.write(json.dumps(utils.format_value(attachments)))

    if not os.path.exists(os.path.join(utils.DATA_DIR, 'attachments', page_id + '_contents')):
        os.mkdir(os.path.join(utils.DATA_DIR, 'attachments', page_id + '_contents'))
    for attachment in attachments:
        with open(os.path.join(utils.DATA_DIR, 'attachments', page_id + '_contents', attachment['id']),
                  'wb') as content_file:
            content_file.write(old_confluence_api.getAttachmentData(page_id, attachment['fileName'], '0').data)


def dump_attachments():
    batch_dump('attachments', dump_attachments_for_page)
