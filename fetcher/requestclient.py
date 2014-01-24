# -*- coding: utf-8 -*-
'''
use request for http client, reference:http://docs.python-requests.org/en/latest/user/quickstart/
'''

import logging
import requests
import copy
from cccrawler.utils import urlutils
from cccrawler.fetcher import client
from miracle.common.utils.gettextutils import _  # noqa
from miracle.common.base import log as clogging
try:
    import json
except ImportError:
    import simplejson as json

from cccrawler.fetcher import client
LOG = clogging.getLogger(__name__)

class HTTPClient(client.HttpClient):
    def __init__(self):
        super(HTTPClient,self).__init__()
        self._logger = logging.getLogger(__name__)

        if self.http_log_debug and not self._logger.handlers:
            # Logging level is already set on the root logger
            ch = logging.StreamHandler()
            self._logger.addHandler(ch)
            self._logger.propagate = False
            if hasattr(requests, 'logging'):
                rql = requests.logging.getLogger(requests.__name__)
                rql.addHandler(ch)
                # Since we have already setup the root logger on debug, we
                # have to set it up here on WARNING (its original level)
                # otherwise we will get all the requests logging messanges
                rql.setLevel(logging.WARNING)
        # requests within the same session can reuse TCP connections from pool
        self.http = requests.Session()

    def fetch(self,request):
        resp = self.request(url = request.url, method = request.method)
        client_resp = client.Response()
        client_resp.code = resp.status_code
        client_resp.reason = resp.reason
        client_resp.history = copy.copy(resp.history)
        client_resp.header = copy.copy(resp.headers)
        client_resp.content = resp.text
        for key,value in resp.headers.items():
            if key.lower() == 'content-type':
                client_resp.content_type = value
        client_resp.orig_encoding = resp.encoding
        return client_resp

    def request(self, url, method, **kwargs):
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.user_agent
        kwargs['headers']['Accept'] = ','.join(self.accept_types)
        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']
#        if self.timeout is not None:
#            kwargs.setdefault('timeout', self.timeout)
#        kwargs['verify'] = self.verify_cert
#         kwargs['allow_redirects'] = True
#        url = urlutils.normalize_url(url)
        self.http_log_req(method, url, kwargs)
        resp = self.http.request(
            method = method,
            url = url,
            allow_redirects=True,
            **kwargs)
        self.http_log_resp(resp)
        if resp.encoding == 'none' or resp.encoding == 'ISO-8859-1':
            resp.encoding = urlutils.get_charset_from_metadata(resp.text)
        LOG.debug(_("request get encoding: %(encoding)s reason: %(reason)s history: %(history)s"
                    " elapsed: %(elapsed)s cookies: %(cookies)s headers: %(headers)s status_code: %(status_code)s"
                    " url: %(url)s"),
                      {'encoding':resp.encoding,
                       'reason':resp.reason,
                       'history':resp.history,
                       'elapsed':resp.elapsed,
                       'cookies':resp.cookies,
                       'headers':resp.headers,
                       'url':resp.url,
                       'status_code':resp.status_code})
#        LOG.debug(_("request get text: %(text)s"),{'text':resp.text})
        return resp

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)

