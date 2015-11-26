# coding=utf-8

import xmlrpc.client
import functools

BASE_URL = 'http://host/rpc/xmlrpc'
USERNAME = 'username'
PASSWORD = 'password'


class ConfluenceAPI(object):

    def __init__(self, base_url, username, password):
        self._cli = xmlrpc.client.Server(base_url)
        self._token = self._cli.confluence1.login(username, password)

    def __getattr__(self, name):
        cli_c = getattr(self._cli, 'confluence1')
        return functools.partial(getattr(cli_c, name), self._token)


confluence_api = ConfluenceAPI(BASE_URL, USERNAME, PASSWORD)
