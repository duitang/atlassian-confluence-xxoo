# coding=utf-8

import xmlrpc.client
import functools

BASE_URL = 'http://host/rpc/xmlrpc'
USERNAME = 'username'
PASSWORD = 'password'

NEW_BASE_URL = 'http://10.1.2.155:8090/rpc/xmlrpc'
NEW_USERNAME = 'username'
NEW_PASSWORD = 'password'


class ConfluenceAPI(object):

    def __init__(self, base_url, username, password):
        self._cli = xmlrpc.client.Server(base_url)
        self._token = self._cli.confluence1.login(username, password)

    def __getattr__(self, name):
        cli_c = getattr(self._cli, 'confluence1')
        return functools.partial(getattr(cli_c, name), self._token)

class Confluence2API(object):

    def __init__(self, base_url, username, password):
        self._cli = xmlrpc.client.Server(base_url)
        self._token = self._cli.confluence1.login(username, password)

    def __getattr__(self, name):
        cli_c = getattr(self._cli, 'confluence2')
        return functools.partial(getattr(cli_c, name), self._token)

old_confluence_api = ConfluenceAPI(BASE_URL, USERNAME, PASSWORD)

new_confluence_api = Confluence2API(NEW_BASE_URL, NEW_USERNAME, NEW_PASSWORD)
