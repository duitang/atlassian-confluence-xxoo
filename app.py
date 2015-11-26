# coding=utf-8

import logging
import logging.config
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
            'filename': 'debug.log',
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

from api import confluence_api
import exporter


logger = logging.getLogger(__name__)



def shell():
    confluence_api.getServerInfo()
    confluence_api.getSpaces()
    confluence_api.getSpace('duitang')
    confluence_api.getPage('425988')
    confluence_api.getPageHistory('425988')
    confluence_api.getAttachments('425988')
    confluence_api.getChildren('425988')
    confluence_api.getComments('425988')

    import IPython
    IPython.embed()


def test():
    pages = exporter.load_pages()
    ordered_pages = exporter.sort_pages(pages)
    exporter.dump_page(ordered_pages[0])


if __name__ == '__main__':
    logger.info('XXX')

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=[
        'dump_page_list', 'dump_pages',
        'test', 'shell',
    ])
    args = parser.parse_args()

    logger.info('Server info: %s' % confluence_api.getServerInfo())

    if args.action == 'dump_page_list':
        exporter.dump_page_list()
    elif args.action == 'dump_pages':
        exporter.dump_pages()  # too long
        pass
    elif args.action == 'test':
        test()
    else:
        shell()
