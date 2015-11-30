# coding=utf-8

import logging
import logging.config
import importer

logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
        },
        'debug': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'full',
            'filename': 'logs/debug.log',
        },

    },
    'formatters': {
        'brief': {'format': '%(message)s', 'datefmt': '%Y%m%d %H:%M:%S',},
        'default': {
            'format': '%(asctime)s [%(levelname)s]  %(name)s -  %(message)s',
            'datefmt': '%Y%m%d %H:%M:%S',
        },
        'full': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%Y%m%d %H:%M:%S',
        },
    },
    'loggers': {
    },
    'root': {
        'handlers': ['console', 'debug'],
        'level': 'INFO'
    },
})
import argparse

from api import old_confluence_api, new_confluence_api
import exporter
import utils


logger = logging.getLogger(__name__)



def shell():
    old_confluence_api.getServerInfo()
    old_confluence_api.getSpaces()
    old_confluence_api.getSpace('duitang')
    old_confluence_api.getPage('425988')
    old_confluence_api.getPageHistory('425988')
    old_confluence_api.getAttachments('425988')
    old_confluence_api.getAttachments('3572309')
    old_confluence_api.getChildren('425988')
    old_confluence_api.getComments('425988')

    import IPython
    IPython.embed()


def test():
    pages = utils.load_pages()
    ordered_pages = utils.sort_pages(pages)
    page = ordered_pages[4]
    old_parent_id_title = dict([(x['id'], x['title']) for x in pages])
    if not page['parentId'] in old_parent_id_title and not page['parentId'] == '0':
        logger.error('No old parent, title: %s, old page id: %s' % (page['title'],
                                                                    page['parentId']))
        return
    if page['parentId'] == '0':
        new_parent_id = '0'
    else:
        new_parent_id = new_confluence_api.getPage('DT', old_parent_id_title[page['parentId']])
    logger.info(page)
    importer.import_page(page['id'], new_parent_id)


if __name__ == '__main__':
    logger.info('XXX')

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=[
        'dump_page_list', 'dump_pages', 'dump_comments', 'dump_attachments',
        'test', 'shell',
    ])
    args = parser.parse_args()

    logger.info('Server info: %s' % old_confluence_api.getServerInfo())

    if args.action == 'dump_page_list':
        exporter.dump_page_list()
    elif args.action == 'dump_pages':
        exporter.dump_pages()  # too long
    elif args.action == 'dump_comments':
        exporter.dump_comments()  # too long
    elif args.action == 'dump_attachments':
        exporter.dump_attachments()
    elif args.action == 'import_pages':
        pass
    elif args.action == 'test':
        test()
    else:
        shell()
