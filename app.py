# coding=utf-8

import logging
import logging.config

logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
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
        'level': 'DEBUG'
    },
})
import argparse

import importer
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
    exporter.dump_page('4358662')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=[
        'dump_page_list', 'dump_pages', 'dump_comments', 'dump_attachments', 'import_pages',
        'import_attachments', 'import_comments',
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
        importer.import_pages()
    elif args.action == 'import_attachments':
        importer.import_attachments()
    elif args.action == 'import_comments':
        importer.import_comments()
    elif args.action == 'test':
        test()
    else:
        shell()

